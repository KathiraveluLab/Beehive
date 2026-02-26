import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app


# JWT creation
def create_access_token(user_id, role="user"):
    expire_hours = current_app.config.get("JWT_EXPIRE_HOURS", 24)
    jwt_secret = current_app.config.get("JWT_SECRET", "dev-secret-change-this")
    jwt_algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")

    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expire_hours),
    }

    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)


# JWT verification
def verify_jwt(token):
    try:
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


# Auth decorator
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        token = auth_header.replace("Bearer ", "")

        try:
            claims = verify_jwt(token)
        except ValueError:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.current_user = {
            "id": claims["sub"],
            "role": claims.get("role", "user"),
        }

        return f(*args, **kwargs)

    return wrapper


# Admin-only decorator
def require_admin_role(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        token = auth_header.replace("Bearer ", "")

        try:
            claims = verify_jwt(token)
        except ValueError:
            return jsonify({"error": "Invalid or expired token"}), 401

        if claims.get("role") != "admin":
            return jsonify({"error": "Admin role required"}), 403

        request.current_user = {
            "id": claims["sub"],
            "role": claims["role"],
        }

        return f(*args, **kwargs)

    return wrapper