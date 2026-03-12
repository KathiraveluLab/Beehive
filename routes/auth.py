import re
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from utils.validation import validate_email, validate_otp, sanitize_string, ValidationError
from database.databaseConfig import db
from database.userdatahandler import update_last_seen
from utils.roles import is_admin_email
from utils.jwt_auth import create_access_token
from database.databaseConfig import beehive

auth_bp = Blueprint("auth", __name__)

OTP_VERIFICATION_WINDOW_SECONDS = 600  # 10 minutes


def _validate_otp_verification(email: str):
    """Check that a valid, unexpired OTP verification session exists for email.

    Returns a Flask response tuple (jsonify(...), status_code) if validation
    fails, or None if the email is properly verified.
    """
    otp_record = db.email_otps.find_one(
        {"email": email, "verified": True},
        sort=[("verified_at", -1)],
    )
    if not otp_record:
        return (
            jsonify({"error": "Email not verified. Please complete OTP verification first."}),
            403,
        )

    verified_at = otp_record.get("verified_at")
    if not verified_at:
        return (
            jsonify({"error": "Invalid verification session. Please restart signup."}),
            403,
        )

    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    if (datetime.now(timezone.utc) - verified_at).total_seconds() > OTP_VERIFICATION_WINDOW_SECONDS:
        db.email_otps.delete_many({"email": email})
        return (
            jsonify({"error": "Verification session expired. Please restart signup."}),
            403,
        )

    return None

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
    try: 
        purpose = sanitize_string(data.get("purpose"), field_name="purpose").lower()
        email = validate_email(data.get("email"))
    except ValidationError as e:
        current_app.logger.warning("Request OTP validation error")
        return jsonify({"error": str(e)}), 400
    existing_user = db.users.find_one({"email": email})

    if purpose == "signup":
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

    elif purpose == "reset":
        if not existing_user:
            return jsonify({"message": "If account exists, OTP sent"}), 200

    else:
        return jsonify({"error": "Invalid purpose"}), 400

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
            return jsonify({"message": "OTP stored (mail not configured)"}), 200
    except Exception as e:
        current_app.logger.exception("Failed to send OTP email: %s", e)
        return jsonify({"message": "OTP stored (failed to send email)"}), 200


from datetime import datetime, timezone

@auth_bp.route("/verify-otp", methods=["POST"], strict_slashes=False)
def verify_otp():
    try:
        data = request.get_json(force=True)
        try: 
            email = validate_email(data.get("email"))
            otp = validate_otp(data.get("otp"))
        except ValidationError as e:  
            current_app.logger.warning("OTP validation error")
            return jsonify({"error": str(e)}), 400

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

        # Mark email as verified instead of deleting
        # This flag is checked by complete-signup to prevent OTP bypass
        # Use _id to target the exact validated record, not just email
        db.email_otps.update_one(
            {"_id": record["_id"]},
            {"$set": {"verified": True, "verified_at": datetime.now(timezone.utc)}},
        )

        return jsonify({"message": "OTP verified"}), 200

    except Exception as e:
        current_app.logger.error(f"VERIFY OTP ERROR: {e}")
        return jsonify({"error": "Server error"}), 500


@auth_bp.route("/complete-signup", methods=["POST"])
def complete_signup():
    data = request.get_json(force=True)

    try:
        email = validate_email(data.get("email"))
        username = sanitize_string(data.get("username"))
        # Check for differentiating usernames and emails, prevent @ in username
        if("@" in username):
            return jsonify({"error": "Username cannot contain '@' symbol"}), 400
        password = sanitize_string(data.get("password"))
    except ValidationError as e:
        current_app.logger.warning("SIGNUP VALIDATION ERROR")
        return jsonify({"error": str(e)}), 400

    # Validate password length
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    # Verify OTP session before creating the account
    otp_error = _validate_otp_verification(email)
    if otp_error:
        return otp_error

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

    try:
        identifier = sanitize_string(data.get("username"))
        if identifier and "@" in identifier:
            identifier = validate_email(identifier)
        password = sanitize_string(data.get("password"))
    except ValidationError as e:
        current_app.logger.warning("LOGIN VALIDATION ERROR")
        return jsonify({"error": str(e)}), 400

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
    update_last_seen(user["_id"])
    return jsonify({"access_token": token}), 200


@auth_bp.route("/set-password", methods=["POST"])
def set_password():
    data = request.get_json(force=True)

    try:
        email = validate_email(data.get("email"))
        password = sanitize_string(data.get("password"))
        purpose = sanitize_string(data.get("purpose"), field_name="purpose").lower()
    except ValidationError as e:
        current_app.logger.warning("SET PASSWORD VALIDATION ERROR")
        return jsonify({"error": str(e)}), 400

    if purpose not in ("signup", "reset"):
        return jsonify({"error": "Invalid purpose. Must be 'signup' or 'reset'."}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    existing_user = db.users.find_one({"email": email})

    if purpose == "signup":
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Verify OTP session before creating the account
        otp_error = _validate_otp_verification(email)
        if otp_error:
            return otp_error

        role = "admin" if is_admin_email(email) else "user"

        user_id = db.users.insert_one({
            "email": email,
            "username": email.split("@")[0],
            "password": hashed,
            "role": role,
            "created_at": datetime.now(timezone.utc)
        }).inserted_id

        # Cleanup OTPs
        db.email_otps.delete_many({"email": email})

    elif purpose == "reset":
        if not existing_user:
            return jsonify({"error": "User not found"}), 404

        # Verify OTP session before allowing password reset
        otp_error = _validate_otp_verification(email)
        if otp_error:
            return otp_error

        db.users.update_one(
            {"email": email},
            {"$set": {"password": hashed}}
        )

        # Cleanup OTPs after successful reset
        db.email_otps.delete_many({"email": email})

        user_id = existing_user["_id"]
        role = existing_user.get("role", "user")

    else:
        return jsonify({"error": "Invalid purpose"}), 400

    token = create_access_token(
        user_id=str(user_id),
        role=role
    )

    return jsonify({
        "access_token": token,
        "role": role
    }), 200

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
