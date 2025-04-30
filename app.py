from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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