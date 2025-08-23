import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clerk Configuration
    CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'beehive-secret-key')
    UPLOAD_FOLDER = 'static/uploads'
    PDF_THUMBNAIL_FOLDER = 'static/uploads/thumbnails/'
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'beehive')
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        if not Config.CLERK_SECRET_KEY:
            raise ValueError("Missing required environment variable: CLERK_SECRET_KEY")
        return True
