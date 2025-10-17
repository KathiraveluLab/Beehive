import base64
from functools import wraps
from flask import json, jsonify, request, session, render_template
from database.admindatahandler import is_admin
from database.userdatahandler import get_user_by_username

# Shared decorators to prevent circular imports

def login_is_required(function):
    @wraps(function)
    def login_wrapper(*args, **kwargs):
        if "google_id" not in session:
            return "Unauthorized", 401
        else:
            return function(*args, **kwargs)
    return login_wrapper



def require_admin_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        # Remove 'Bearer ' prefix if present
        token = auth_header[7:] if auth_header.startswith('Bearer ') else auth_header

        try:
            parts = token.split('.')
            if len(parts) != 3:
                return jsonify({'error': 'Invalid token format'}), 401

            # Decode the payload (second part)
            payload = parts[1]
            payload += '=' * (-len(payload) % 4)  # pad if needed

            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded = json.loads(decoded_bytes.decode('utf-8'))

            user_role = decoded.get('role', 'user')

            # Allow only if admin
            if user_role != 'admin':
                return jsonify({'error': 'Forbidden: admin role required'}), 403

            # Continue if role matches
            return f(*args, **kwargs)

        except Exception as e:
            print("Token decode error:", e)
            return jsonify({'error': 'Invalid token'}), 401

    return decorated_function
