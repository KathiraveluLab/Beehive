import email
import re
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, timezone
import random
import secrets
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database.databaseConfig import db
from database.userdatahandler import create_user, get_user_by_username
from utils.roles import is_admin_email
from utils.jwt_auth import create_access_token
from database.databaseConfig import beehive

auth_bp = Blueprint("auth", __name__)

# Create EMAIL OTP
def create_email_otp(email: str) -> str:
    otp = str(secrets.randbelow(900000) + 100000)

    # Remove old OTPs
    db.email_otps.delete_many({"email": email})
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    db.email_otps.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": expires_at
        })

    return otp


# REQUEST OTP 
@auth_bp.route("/request-otp", methods=["POST"])
def request_otp():
    data = request.get_json(force=True)
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400
    existing_user = db.users.find_one({"email": email})

    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    otp = create_email_otp(email)

    # send the OTP via email
    try:
        mail_username = current_app.config.get("MAIL_USERNAME")
        mail_server = current_app.config.get("MAIL_SERVER")
        if mail_username and mail_server:
            from flask_mail import Message
            from app import mail

            subject = "Your Beehive OTP"
            body = f"Your Beehive verification code is: {otp}\nIt will expire in 5 minutes."
            msg = Message(subject=subject, recipients=[email], body=body, sender=mail_username)
            mail.send(msg)
            return jsonify({"message": "OTP sent"}), 200
        else:
            current_app.logger.info("MAIL not configured, printing OTP to console")
            print("EMAIL OTP:", otp)
            return jsonify({"message": "OTP stored (mail not configured)"}), 200
    except Exception as e:
        current_app.logger.exception("Failed to send OTP email: %s", e)
        return jsonify({"message": "OTP stored (failed to send email)"}), 200


from datetime import datetime, timezone

@auth_bp.route("/verify-otp", methods=["POST"], strict_slashes=False)
def verify_otp():
    try:
        data = request.get_json(force=True)

        email = data.get("email")
        otp = data.get("otp")

        if not email or not otp:
            return jsonify({"error": "Email and OTP required"}), 400

        record = db.email_otps.find_one({
            "email": email,
            "otp": str(otp)
        })

        if not record:
            return jsonify({"error": "Invalid OTP"}), 400

        expires_at = record["expires_at"]

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            return jsonify({"error": "OTP expired"}), 400

        return jsonify({"message": "OTP verified"}), 200

    except Exception as e:
        print("VERIFY OTP ERROR:", e)
        return jsonify({"error": "Server error"}), 500


@auth_bp.route("/complete-signup", methods=["POST"])
def complete_signup():
    data = request.get_json(force=True)

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"error": "Missing fields"}), 400
    # Validate email format
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400
    # Validate password length
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    # Prevent duplicate email
    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400
    # Prevent duplicate username
    if db.users.find_one({"username": username}):
        return jsonify({"error": "Username already taken"}), 400

    role = "admin" if is_admin_email(email) else "user"

    hashed_password = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    )

    result = db.users.insert_one({
        "email": email,
        "username": username,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    })

    token = create_access_token(
        user_id=str(result.inserted_id),
        role=role
    )

    # Cleanup OTPs
    db.email_otps.delete_many({"email": email})

    return jsonify({
        "access_token": token,
        "role": role
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    identifier = data.get("username")  # username OR email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "Username/email and password required"}), 400

    user = beehive.users.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })

    if not user:
        return jsonify({"error": "User not found"}), 401

    stored_password = user.get("password")
    if not stored_password:
        return jsonify({"error": "Password not set"}), 400

    if not bcrypt.checkpw(password.encode(), stored_password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        user_id=str(user["_id"]),
        role=user.get("role", "user")
    )

    return jsonify({"access_token": token}), 200


@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    data = request.get_json(force=True)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    role = "admin" if is_admin_email(email) else "user"

    user_id = db.users.insert_one({
        "email": email,
        "username": email.split("@")[0],
        "password": hashed,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }).inserted_id

    token = create_access_token(
        user_id=str(user_id),
        role=role
    )

    db.email_otps.delete_many({"email": email})

    return jsonify({
        "access_token": token,
        "role": role
    }), 201

# GOOGLE OAUTH (JWT ONLY)
@auth_bp.route("/google", methods=["POST"])
def google_auth():
    data = request.get_json(force=True)

    id_token_str = data.get("id_token")
    if not id_token_str:
        return jsonify({"error": "id_token required"}), 400

    try:
        request_adapter = google_requests.Request()
        client_id = current_app.config.get("GOOGLE_CLIENT_ID")
        # Verify the token and audience
        idinfo = id_token.verify_oauth2_token(id_token_str, request_adapter, client_id)

        # idinfo now contains verified claims
        email = idinfo.get("email")
        name = idinfo.get("name") or idinfo.get("given_name")
        sub = idinfo.get("sub")

        if not email:
            return jsonify({"error": "Email not present in token"}), 400

        if not idinfo.get("email_verified"):
            return jsonify({"error": "Email not verified"}), 403


    except ValueError as e:
        current_app.logger.exception("Invalid Google ID token: %s", e)
        return jsonify({"error": "Invalid id_token"}), 401

    # At this point the token is verified; trust the email claim
    user = db.users.find_one({"email": email})

    if not user:
        role = "admin" if is_admin_email(email) else "user"

        # Create a minimal Google-backed user (no local password)
        result = db.users.insert_one({
            "email": email,
            "username": name or email.split("@")[0],
            "password": None,
            "role": role,
            "provider": "google",
            "google_id": sub,
            "created_at": datetime.now(timezone.utc)
        })
        user_id = str(result.inserted_id)
    else:
        user_id = str(user["_id"])
        role = user.get("role", "user")

    token = create_access_token(user_id=user_id, role=role)

    return jsonify({
        "access_token": token,
        "role": role
    }), 200
