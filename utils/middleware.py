from flask import request, jsonify
from functools import wraps
from config import Config

def handle_cors(f):
    """Middleware to handle CORS preflight requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin')
            # Only allow whitelisted origins
            if origin in Config.CORS_ORIGINS:
                response = jsonify({'status': 'ok'})
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
                response.headers.add('Access-Control-Max-Age', '3600')
                return response
            else:
                # Reject requests from non-whitelisted origins
                return jsonify({'error': 'Origin not allowed'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def add_auth_headers(response):
    """Add authentication-related headers to responses"""
    origin = request.headers.get('Origin')
    # Only add CORS headers for whitelisted origins
    if origin in Config.CORS_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
