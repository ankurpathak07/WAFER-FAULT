from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
app.permanent_session_lifetime = timedelta(days=7)  # Session expires after 7 days

# Temporary user storage (replace with database in production)
users = {
    'admin@silifault.com': {
        'password': generate_password_hash('admin123'),
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
            
        if email in users:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        # Create new user
        users[email] = {
            'password': generate_password_hash(password),
            'name': name
        }
        
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
            
        if email in users and check_password_hash(users[email]['password'], password):
            session['user'] = email
            session['name'] = users[email]['name']
            if remember:
                session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('upload_page'))
        else:
            flash('Invalid email or password', 'error')
    
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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the file temporarily or process it
        # Here you would normally add your AI processing logic
        # For demo purposes, we'll just return a success message
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': file.filename,
            'defects_detected': 3,
            'accuracy': 99.7
        })

if __name__ == '__main__':
    app.run(debug=True) 