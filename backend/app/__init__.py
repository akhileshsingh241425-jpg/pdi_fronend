from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['PDF_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'generated_pdfs')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes.ipqc_routes import ipqc_bp
    app.register_blueprint(ipqc_bp, url_prefix='/api')
    
    return app
