import bcrypt


def test_request_otp_reset_failure(client, mock_db):
    """POST /api/auth/request-otp - Not existing user"""

    response = client.post(
        "/api/auth/request-otp", json={"email": "test1@example.com", "purpose": "reset"}
    )

    assert response.status_code == 200  # security purposes
    data = response.get_json()
    assert data["message"] == "If account exists, OTP sent"


def test_request_otp_signup_success(client, mock_db):
    """POST /api/auth/request-otp"""

    response = client.post(
        "/api/auth/request-otp", json={"email": "test@example.com", "purpose": "signup"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert (
        data["message"].startswith("OTP stored")
    )  # since we are not actually sending emails in tests


def test_request_otp_signup_failure(client, mock_db):
    """POST /api/auth/request-otp - Not existing user"""
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one(
        {"email": "test@example.com", "username": "testuser", "password": hashed_pw}
    )

    response = client.post(
        "/api/auth/request-otp", json={"email": "test@example.com", "purpose": "signup"}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email already registered"
