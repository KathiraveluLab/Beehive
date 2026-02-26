import os
import requests
from functools import wraps
from flask import request, jsonify
import jwt
from jwt import PyJWKClient

CLERK_JWKS_URL = "https://api.clerk.com/v1/.well-known/jwks.json"
jwks_client = PyJWKClient(CLERK_JWKS_URL)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_signature": True, "verify_exp": True}
            )
            user_id = decoded.get('sub')
            if not user_id:
                return jsonify({'error': 'No user ID in token'}), 401
            request.current_user = {
                'id': user_id,
                'userid': user_id
            }
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidSignatureError:
            return jsonify({'error': 'Invalid token signature'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    return decorated_function