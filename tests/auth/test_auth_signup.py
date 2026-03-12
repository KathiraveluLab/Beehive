import pytest
import mongomock
from unittest.mock import patch
import bcrypt
from datetime import datetime, timedelta, timezone

def test_complete_signup_success(client, mock_db):
    """POST /api/auth/complete-signup"""
    response = client.post("/api/auth/complete-signup", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })

    user = mock_db.users.find_one({"email": "test@example.com"})

    assert response.status_code == 201
    data = response.get_json()
    assert user is not None
    assert user["username"] == "testuser"
    assert bcrypt.checkpw(b"testpassword", user["password"])
    assert "access_token" in data
    assert "role" in data
    assert data["role"] == "user"


def test_request_otp_reset_success(client, mock_db):
    """POST /api/auth/request-otp"""
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw
    })

    response = client.post("/api/auth/request-otp", json={
        "email": "test@example.com",
        "purpose": "reset"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "OTP stored (failed to send email)" # since we are not actually sending emails in tests
