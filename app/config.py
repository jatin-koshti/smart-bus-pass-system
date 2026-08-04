import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-codealpha-smart-bus-2026')
    
    # Handle DB URI compatibility for PostgreSQL vs SQLite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///smart_bus_pass.db')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for QR code cache if saved to disk
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads', 'qr_codes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
