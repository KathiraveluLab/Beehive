"""
Security middleware for Flask application
Provides CSRF protection, rate limiting, input validation, and security headers
"""
import os
import jwt
import bleach
import validators
from functools import wraps
from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect


class SecurityConfig:
    """Security configuration and utilities"""
    
    @staticmethod
    def get_jwt_secret():
        """Get JWT secret from environment"""
        secret = os.getenv('JWT_SECRET_KEY') or os.getenv('FLASK_SECRET_KEY')
        if not secret:
            raise ValueError('JWT_SECRET_KEY or FLASK_SECRET_KEY must be set')
        return secret
    
    @staticmethod
    def validate_jwt_token(token):
        """Validate JWT token with proper signature verification"""
        try:
            secret = SecurityConfig.get_jwt_secret()
            decoded = jwt.decode(token, secret, algorithms=['HS256'])
            return decoded
        except jwt.InvalidTokenError:
            return None


class InputValidator:
    """Input validation and sanitization utilities"""
    
    @staticmethod
    def sanitize_html(content):
        """Sanitize HTML content to prevent XSS"""
        if not content:
            return content
        return bleach.clean(content, tags=['p', 'br', 'strong', 'em'], strip=True)
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        return validators.email(email)
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""  
        if not url:
            return False
        return validators.url(url)


def init_security_middleware(app):
    """Initialize security middleware for Flask app"""
    
    # CSRF Protection
    csrf = CSRFProtect(app)
    
    # Rate Limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Security Headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    return {'csrf': csrf, 'limiter': limiter}


def require_auth(f):
    """Decorator to require valid JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_data = SecurityConfig.validate_jwt_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        g.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function
