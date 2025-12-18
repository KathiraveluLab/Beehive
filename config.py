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
    _cors_origins_env = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]
    
    # Rate Limiting Configuration
    # For production/multi-worker deployments, use Redis (redis://redis:6379/0)
    # For development (single worker), memory:// is acceptable but NOT recommended for production
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
    RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "redis://redis:6379/0")
    # Endpoint-specific overrides
    RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "10/minute")
    RATE_LIMIT_ANALYZE_MEDIA = os.getenv("RATE_LIMIT_ANALYZE_MEDIA", "20/minute")
    RATE_LIMIT_CHAT_SEND = os.getenv("RATE_LIMIT_CHAT_SEND", "60/minute")
    RATE_LIMIT_CHAT_MESSAGES = os.getenv("RATE_LIMIT_CHAT_MESSAGES", "120/minute")
    RATE_LIMIT_EDIT_DELETE = os.getenv("RATE_LIMIT_EDIT_DELETE", "30/minute")
    RATE_LIMIT_NOTIFICATIONS = os.getenv("RATE_LIMIT_NOTIFICATIONS", "60/minute")
    RATE_LIMIT_GET_UPLOADS = os.getenv("RATE_LIMIT_GET_UPLOADS", "60/minute")
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        if not Config.CLERK_SECRET_KEY:
            raise ValueError("Missing required environment variable: CLERK_SECRET_KEY")
        return True
