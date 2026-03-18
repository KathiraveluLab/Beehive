import bcrypt
import pytest
from datetime import datetime, timedelta, timezone


@pytest.fixture
def created_user(mock_db):
    """Fixture to create a user in the mock database."""
    password = "securepassword"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw,
    }
    mock_db.users.insert_one(user_data)
    return {"email": user_data["email"], "password": password}


def test_request_otp_invalid_purpose(client):
    """POST /api/auth/request-otp - Invalid purpose"""
    response = client.post(
        "/api/auth/request-otp",
        json={
            "email": "test@example.com",
            "purpose": "invalid_purpose"
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid purpose"


def test_request_otp_signup_success(client):
    """POST /api/auth/request-otp"""

    response = client.post(
        "/api/auth/request-otp", json={"email": "test@example.com", "purpose": "signup"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"].startswith("OTP stored") # since we are not actually sending emails in tests


def test_request_otp_signup_failure(client, created_user):
    """POST /api/auth/request-otp - Not existing user"""
    response = client.post(
        "/api/auth/request-otp",
        json={
            "email": created_user["email"],
            "purpose": "signup",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email already registered"


def test_request_otp_reset_success(client, created_user):
    """POST /api/auth/request-otp - existing user"""

    response = client.post(
        "/api/auth/request-otp",
          json={
              "email": created_user["email"],
              "purpose": "reset"
        },
    )

    assert response.status_code == 200  # security purposes
    data = response.get_json()
    assert data["message"].startswith("OTP stored")  # since we are not actually sending emails in tests


def test_request_otp_reset_failure(client):
    """POST /api/auth/request-otp - Not existing user"""

    response = client.post(
        "/api/auth/request-otp", json={"email": "test1@example.com", "purpose": "reset"}
    )

    assert response.status_code == 200  # security purposes
    data = response.get_json()
    assert data["message"] == "If account exists, OTP sent"


def test_verify_otp_success(client, mock_db):
    """POST /api/auth/verify-otp"""
    email = "test@example.com"
    otp = "123456"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    mock_db.email_otps.insert_one(
        {"email": email, "otp": otp, "expires_at": expires_at}
    )

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": email,
            "otp": otp,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "OTP verified"


def test_verify_otp_failure(client):
    """POST /api/auth/verify-otp - Invalid OTP"""

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": "test@example.com",
            "otp": "000000",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid OTP"


def test_verify_otp_expired(client, mock_db):
    """POST /api/auth/verify-otp - Expired OTP"""
    email = "test@example.com"
    otp = "123456"
    expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)

    mock_db.email_otps.insert_one(
        {"email": email, "otp": otp, "expires_at": expires_at}
    )

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": email,
            "otp": otp,
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "OTP expired"