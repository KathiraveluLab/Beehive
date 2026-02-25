import os
import requests
import base64
import json
from datetime import datetime
from functools import wraps
from flask import request, jsonify
from authlib.jose import jwt, JoseError

def require_auth(f):
    """Simple decorator to check if user is authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        # Remove 'Bearer ' prefix if present
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
            
        try:
            public_key = os.getenv('CLERK_JWT_PUBLIC_KEY')
            
            try:
                if public_key:
                    decoded = jwt.decode(token, public_key)
                    decoded.validate()
                else:
                    parts = token.split('.')
                    if len(parts) != 3:
                        return jsonify({'error': 'Invalid token format'}), 401
                    
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
                    
                    if 'exp' in decoded:
                        if datetime.fromtimestamp(decoded['exp']) < datetime.now():
                            return jsonify({'error': 'Token has expired'}), 401
                
                user_id = decoded.get('sub') or decoded.get('userid')
                
                if not user_id:
                    return jsonify({'error': 'No user ID in token'}), 401
                
                request.current_user = {
                    'id': user_id,
                    'userid': user_id
                }
                return f(*args, **kwargs)
                
            except JoseError as je:
                return jsonify({'error': f'Token verification failed: {str(je)}'}), 401
            except Exception as decode_error:
                return jsonify({'error': 'Invalid token format'}), 401
            
        except Exception as e:
            print("General Exception:", str(e))
            print("Exception type:", type(e).__name__)
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function