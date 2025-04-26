# SiliFault - Advanced Wafer Defect Detection

A modern web application for AI-powered wafer defect detection with Flask backend integration.

## Project Overview

SiliFault is a showcase application demonstrating how AI can be used in semiconductor manufacturing for wafer defect detection and analysis. The application features a responsive frontend built with HTML, CSS, and JavaScript, connected to a Flask backend.

## Features

- Modern, responsive UI with subtle animations
- Elegant color palette (Smoky Black, Olive Drab, Bone, and Floral White)
- Circuit board hero background image
- Drag and drop file upload functionality
- Flask backend integration for file processing
- Interactive feature showcase
- Mobile-friendly design

## Project Structure

```
├── app.py              # Main Flask application
├── static/             # Static files
│   ├── css/            # CSS stylesheets
│   │   └── style.css   # Main stylesheet
│   ├── js/             # JavaScript files
│   │   └── main.js     # Main JavaScript file
│   └── images/         # Image assets
│       ├── circuit-board.jpg # Hero background image
│       └── hero-wafer.svg    # Wafer illustration
├── templates/          # HTML templates
│   ├── base.html       # Base template with common elements
│   └── index.html      # Main page template
└── README.md           # Project documentation
```

## Installation & Running

1. Clone the repository
2. Install the requirements:
   ```
   pip install flask
   ```
3. Make sure to add the circuit board image to `static/images/circuit-board.jpg`
4. Run the Flask application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python, Flask
- **Design**: Responsive design, CSS Grid, Flexbox
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter, Manrope)
- **Color Palette**: Smoky Black (#11120D), Olive Drab (#565449), Bone (#D8CFBC), and Floral White (#FFFBF4)

## Development

This project uses a simple file structure with proper separation of concerns:
- **app.py**: Contains Flask routes and server-side logic
- **static/**: Contains all static assets (CSS, JS, images)
- **templates/**: Contains HTML templates using Jinja2 templating

## Future Enhancements

- Add user authentication
- Implement actual AI processing for wafer images
- Add database integration for storing results
- Create a dashboard for historical analysis
- Implement real-time processing with WebSockets 