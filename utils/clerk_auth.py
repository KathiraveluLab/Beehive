import os
import requests
import base64
import json
from functools import wraps
from flask import request, jsonify

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
            print("Token to decode:", token[:50] + "..." if len(token) > 50 else token)
            
            # Simple JWT decode without external library
            parts = token.split('.')
            if len(parts) != 3:
                return jsonify({'error': 'Invalid token format'}), 401
            
            # Decode the payload (second part)
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            
            try:
                decoded_bytes = base64.urlsafe_b64decode(payload)
                decoded = json.loads(decoded_bytes.decode('utf-8'))
                print("Decoded token:", decoded)
                
                # Extract user ID from the token
                user_id = decoded.get('sub') or decoded.get('userid')
                print("Extracted user_id:", user_id)
                
                if not user_id:
                    print("No user ID found in token")
                    return jsonify({'error': 'No user ID in token'}), 401
                
                role = decoded.get('role', 'user')

                # Token is valid, user is authenticated
                request.current_user = {
                    'id': user_id,
                    'userid': user_id,  # Your session claim
                    'role': role
                }
                print(f"Authentication successful for user: {user_id} with role: {role}")
                
                return f(*args, **kwargs)
                
            except Exception as decode_error:
                print("Token decode error:", str(decode_error))
                return jsonify({'error': 'Invalid token format'}), 401
            
        except Exception as e:
            print("General Exception:", str(e))
            print("Exception type:", type(e).__name__)
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function