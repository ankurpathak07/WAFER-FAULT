from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import re
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt

# Load environment variables
load_dotenv()

class ImprovedCNN(nn.Module):
    def __init__(self, num_classes):
        super(ImprovedCNN, self).__init__()
        
        # Enhanced feature extraction
        self.features = nn.Sequential(
            # First conv block
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), 
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Second conv block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Third conv block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        
        # Adaptive pooling to handle different input sizes
        self.adaptive_pool = nn.AdaptiveAvgPool2d((8, 8))
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(128 * 8 * 8, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# Initialize Flask app and configs
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///wafer_fault.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Initialize SQLAlchemy for database management


# Initialize Flask-Bcrypt for password hashing
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
    
    def __init__(self, email, password, name):
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.name = name
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    
with app.app_context():
    db.create_all()  # Create database tables if they don't exist
        


# Set up model and device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the trained model
checkpoint_path = "model_checkpoint1.pth"
if os.path.exists(checkpoint_path):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    # Get number of classes from the checkpoint
    output_size = checkpoint['model_state_dict']['classifier.8.bias'].size(0)
    model = ImprovedCNN(num_classes=output_size).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    class_names = checkpoint.get('classes', [f'Class_{i}' for i in range(output_size)])  # Default if not saved
else:
    print("Warning: Model checkpoint not found!")
    model = ImprovedCNN(num_classes=9).to(device)  # Default to 9 classes if no checkpoint

# Image transformation pipeline
image_size = 128  # Must match training size
transform = transforms.Compose([
    transforms.Resize((image_size, image_size)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Temporary user storage (replace with database in production)
users = {
    'admin@silifault.com': {
        'password': generate_password_hash('password'),
        'name': 'Admin User'
    }
}

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        # Validation
        if not email or not password or not confirm_password or not name:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
            
        if not is_valid_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('register'))
            
        if not is_valid_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        users = User(email=email, password=password, name=name)
        db.session.add(users)
        db.session.commit()
        
        
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = user.email
            session['name'] = user.name
            session.permanent = remember
            flash('Login successful!', 'success')
            return redirect(url_for('upload_page'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/upload')
def upload_page():
    if 'user' not in session:
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

def predict_image(image_path):
    """Predicts whether a wafer image contains defects."""
    try:
        # Open and preprocess image
        image = Image.open(image_path).convert('L')  # Convert to grayscale
        image_tensor = transform(image).unsqueeze(0).to(device)  # Add batch dimension
        
        # Make prediction
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
        prediction_class = class_names[predicted.item()]
        confidence_score = confidence.item() * 100
        
        return {
            'prediction': prediction_class,
            'confidence': confidence_score,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        # Make prediction
        result = predict_image(file_path)
        print(result)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': file.filename,
                'prediction': result['prediction'],
                'confidence': f"{result['confidence']:.2f}%"
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            company = request.form.get('company')
            subject = request.form.get('subject')
            message = request.form.get('message')

            # Validate form data
            if not all([name, email, company, subject, message]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('contact'))

            # Create email message
            msg = Message(
                subject=f'New Contact Form Submission: {subject}',
                recipients=[os.getenv('ADMIN_EMAIL')],
                body=f'''
                New contact form submission from SiliFault website:
                
                Name: {name}
                Email: {email}
                Company: {company}
                Subject: {subject}
                
                Message:
                {message}
                '''
            )

            # Send email
            mail.send(msg)

            # Send confirmation email to user
            user_msg = Message(
                subject='Thank you for contacting SiliFault',
                recipients=[email],
                body=f'''
                Dear {name},

                Thank you for contacting SiliFault. We have received your message and will get back to you shortly.

                Here's a copy of your message:
                Subject: {subject}
                Message: {message}

                Best regards,
                The SiliFault Team
                '''
            )
            mail.send(user_msg)

            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))

        except Exception as e:
            flash('An error occurred while sending your message. Please try again later.', 'error')
            print(f"Error sending email: {str(e)}")
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/features')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    app.run(debug=True)