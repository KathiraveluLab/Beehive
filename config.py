import os
import sys
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
    _cors_origins_env = os.getenv("CORS_ORIGINS")
    CORS_ORIGINS = [origin.strip() for origin in (_cors_origins_env or "").split(",") if origin.strip()]
    
    # List of insecure/default values that should not be used in production
    INSECURE_DEFAULTS = {
        'beehive-secret-key',
        'dev-secret-change-this',
        'your_jwt_secret_here',
        'your_flask_secret_key_here',
        'your_flask_secret_key_here_CHANGE_THIS',
        'your_jwt_secret_here_CHANGE_THIS',
        'change-me',
        'secret',
    }
    
    @staticmethod
    def validate_config():
        """
        Validate that all required configuration is present and secure.
        Fails fast on startup if critical config is missing or insecure.
        """
        errors = []
        warnings = []
        
        # Required: JWT_SECRET
        if not Config.JWT_SECRET:
            errors.append("JWT_SECRET environment variable is required but not set.")
        elif Config.JWT_SECRET in Config.INSECURE_DEFAULTS:
            errors.append(f"JWT_SECRET is set to an insecure default value. Use a strong, unique secret.")
        elif len(Config.JWT_SECRET) < 32:
            warnings.append(f"JWT_SECRET is too short ({len(Config.JWT_SECRET)} chars). Recommended: 32+ characters.")
        
        # Required: FLASK_SECRET_KEY
        if not Config.SECRET_KEY:
            errors.append("FLASK_SECRET_KEY environment variable is required but not set.")
        elif Config.SECRET_KEY in Config.INSECURE_DEFAULTS:
            errors.append(f"FLASK_SECRET_KEY is set to an insecure default value. Use a strong, unique secret.")
        elif len(Config.SECRET_KEY) < 32:
            warnings.append(f"FLASK_SECRET_KEY is too short ({len(Config.SECRET_KEY)} chars). Recommended: 32+ characters.")
        
        # Required: MONGODB_URI
        if not Config.MONGODB_URI:
            errors.append("MONGODB_URI environment variable is required but not set.")
        elif not Config.MONGODB_URI.startswith(('mongodb://', 'mongodb+srv://')):
            errors.append("MONGODB_URI must start with 'mongodb://' or 'mongodb+srv://'")
        
        # Required: CORS_ORIGINS
        if not Config.CORS_ORIGINS:
            errors.append("CORS_ORIGINS environment variable is required but not set. Specify allowed origins (comma-separated).")
        
        # Print warnings (non-fatal)
        if warnings:
            print("\n⚠️  Configuration Warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"   - {warning}", file=sys.stderr)
            print()
        
        # Print errors and exit if any critical issues found
        if errors:
            print("\n❌ Configuration Validation Failed:", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            for error in errors:
                print(f"   ✗ {error}", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print("\n💡 To fix this:", file=sys.stderr)
            print("   1. Copy .env.example to .env", file=sys.stderr)
            print("   2. Fill in all required values with secure secrets", file=sys.stderr)
            print("   3. Generate strong secrets using: python -c 'import secrets; print(secrets.token_hex(32))'", file=sys.stderr)
            print("\n📖 See docs/setup.md for detailed setup instructions.\n", file=sys.stderr)
            sys.exit(1)
        
        return True
