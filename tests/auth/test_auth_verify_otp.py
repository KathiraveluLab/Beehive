from datetime import datetime, timedelta, timezone


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
            "email": "test@example.com",
            "otp": "123456",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "OTP verified"


def test_verify_otp_failure(client, mock_db):
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
