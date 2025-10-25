import os
import requests
import base64
import json
from functools import wraps
from flask import request, jsonify, session
from database.admindatahandler import  is_admin
from database.userdatahandler import get_currentuser_from_session, get_userid_by_imageid

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
                user_id = decoded.get('sub') or decoded.get('userid') or decoded.get('user_id') # Fix: 'user_id' is the valid field in the image database
                print("Extracted user_id:", user_id)
                
                if not user_id:
                    print("No user ID found in token")
                    return jsonify({'error': 'No user ID in token'}), 401
                
                # Set up session data for compatibility with existing authorization logic
                session['user'] = {
                    'user_id': user_id,
                    '_id': user_id
                }
                # Also set individual session keys that our code expects
                if decoded.get('username'):
                    session['username'] = decoded.get('username')
                if decoded.get('mail_id') or decoded.get('email'):
                    session['email'] = decoded.get('mail_id') or decoded.get('email')
                if decoded.get('role'):
                    session['role'] = decoded.get('role')
                
                print("Session data set:", dict(session))
                
                # Token is valid, user is authenticated
                request.current_user = {
                    'id': user_id,
                    'userid': user_id  # Your session claim
                }
                print("Authentication successful for user:", user_id)
                
                return f(*args, **kwargs)
                
            except Exception as decode_error:
                print("Token decode error:", str(decode_error))
                return jsonify({'error': 'Invalid token format'}), 401
            
        except Exception as e:
            print("General Exception:", str(e))
            print("Exception type:", type(e).__name__)
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

# Authorization done here
def is_owner_or_admin(f):
    """Simple decorator to check user is either the owner of resources or an admin"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        image_id = kwargs.get('image_id') or (args[0] if args else None)
        user_id = kwargs.get('user_id')
        
        if image_id and not user_id:
            from bson import ObjectId
            image_id=ObjectId(image_id)
            
            current_user = get_currentuser_from_session()
            current_user_id = current_user['_id']
            
            image_owner_id = get_userid_by_imageid(image_id)
            image_owner_id = ObjectId(image_owner_id)
            
            if not (current_user_id == image_owner_id or is_admin()):
                print("You are not authorized to make changes")
                return jsonify({'error': 'You are not authorized to make changes.'}), 403
            
            print("User Authorized to make changes")
            
            
        # if user_id is provided instead of image_id
        if user_id and not image_id:
            current_user_id = session['user']['user_id']
            if not (str(current_user_id) == str(user_id) or is_admin()):
                print("You are not authorized to make changes")
                return jsonify({'error': 'You are not authorized to make changes.'}), 403
            print("User Authorized to make changes")
            
            
        return f(*args, **kwargs)
    return wrapper