import os
import json
import threading
import logging
from functools import wraps
from typing import Dict

from flask import request, jsonify

# JWT verification
try:
    import jwt
    from jwt import PyJWKClient
except ImportError:
    jwt = None
    PyJWKClient = None

# Cache for PyJWKClient instances keyed by issuer URL
_jwk_client_cache: Dict[str, "PyJWKClient"] = {}
_jwk_client_cache_lock = threading.Lock()
JWKS_LIFESPAN_SECONDS = 3600

# Validate required environment variables at startup
CLERK_ISSUER = os.getenv('CLERK_ISSUER')
if not CLERK_ISSUER:
    raise RuntimeError('Missing required CLERK_ISSUER environment variable')


def _get_jwk_client(issuer: str):
    """Get or create a cached PyJWKClient for the given issuer."""
    if issuer in _jwk_client_cache:
        return _jwk_client_cache[issuer]
    
    with _jwk_client_cache_lock:
        if issuer not in _jwk_client_cache:
            jwks_url = issuer.rstrip('/') + '/.well-known/jwks.json'
            # PyJWKClient caches keys internally; lifespan controls how long before refresh
            _jwk_client_cache[issuer] = PyJWKClient(jwks_url, lifespan=JWKS_LIFESPAN_SECONDS)
    return _jwk_client_cache[issuer]

def _verify_jwt(token: str):
    """Verify JWT using JWKS from the configured issuer and return claims."""
    if jwt is None or PyJWKClient is None:
        raise ValueError('PyJWT is not installed; cannot verify tokens')

    try:
        jwk_client = _get_jwk_client(CLERK_ISSUER)
        signing_key = jwk_client.get_signing_key_from_jwt(token)

        # Clerk tokens typically use RS256 and include `iss`
        # Verify issuer signature but skip audience verification for compatibility
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "RS512"],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False}
        )
        return claims
    except jwt.PyJWTError as e:
        # Log the actual error for debugging but raise a generic error
        logging.error(f'JWT verification failed: {e}')
        raise ValueError('Token verification failed') from e

def require_auth(f):
    """Decorator to enforce authentication via verified JWT (Clerk)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401

        # Remove 'Bearer ' prefix if present
        token = auth_header[7:] if auth_header.startswith('Bearer ') else auth_header

        try:
            claims = _verify_jwt(token)

            user_id = claims.get('sub') or claims.get('userid')
            if not user_id:
                return jsonify({'error': 'Invalid token: missing subject'}), 401

            # Prefer Clerk public metadata role if present
            role = (
                (claims.get('public_metadata') or {}).get('role')
                or claims.get('role')
                or 'user'
            )

            request.current_user = {
                'id': user_id,
                'role': role,
                'claims': claims,
            }

            return f(*args, **kwargs)

        except ValueError as e:
            # Avoid leaking verification details, return generic auth error
            return jsonify({'error': 'Invalid or unverifiable token'}), 401

    return decorated_function
