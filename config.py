import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 24))

    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    UPLOAD_FOLDER = 'static/uploads'
    PDF_THUMBNAIL_FOLDER = 'static/uploads/thumbnails/'
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'beehive')
    
    # CORS Configuration
    _cors_origins_env = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = {
            'JWT_SECRET': Config.JWT_SECRET,
            'FLASK_SECRET_KEY': Config.SECRET_KEY,
            'MONGODB_URI': Config.MONGODB_URI,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please set these in your .env file or environment."
            )
        
        return True
