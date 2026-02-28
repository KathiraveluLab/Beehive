from flask import request, jsonify
from functools import wraps

def handle_cors(f):
    """Middleware to handle CORS preflight requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
            return response
        
        return f(*args, **kwargs)
    return decorated_function

def add_auth_headers(response):
    """Add authentication-related headers to responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
    return response
