from functools import wraps
from flask import jsonify, request, session

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
    """Enforce verified JWT with admin role (uses JWKS like require_auth).
    
    Requires Authorization: Bearer <JWT> header with valid signature and admin role.
    Sets request.current_user with verified user_id and role on success.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import here to avoid circular imports
        from utils.clerk_auth import _verify_jwt
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        token = auth_header[7:] if auth_header.startswith('Bearer ') else auth_header

        try:
            claims = _verify_jwt(token)
            
            # Extract role from verified claims
            role = (
                (claims.get('public_metadata') or {}).get('role')
                or claims.get('role')
                or 'user'
            )
            
            # Enforce admin role
            if role != 'admin':
                return jsonify({'error': 'Forbidden: admin role required'}), 403
            
            # Extract user ID and set on request for downstream use
            user_id = claims.get('sub') or claims.get('userid')
            if not user_id:
                return jsonify({'error': 'Invalid token: missing subject'}), 401
            
            request.current_user = {
                'id': user_id,
                'role': role,
                'claims': claims,
            }
            
            return f(*args, **kwargs)

        except ValueError as e:
            # Avoid leaking verification details
            return jsonify({'error': 'Invalid or unverifiable token'}), 401

    return decorated_function
