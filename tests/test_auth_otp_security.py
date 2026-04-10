from datetime import datetime, timedelta, timezone

import bcrypt
import pytest

#---- Helpers ----


def _seed_existing_user(
    mock_db, email, username="existing_user", password="OldPass@123"
):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    mock_db.users.insert_one(
        {
            "email": email,
            "username": username,
            "password": hashed,
            "role": "user",
            "created_at": datetime.now(timezone.utc),
        }
    )


def _seed_otp_record(mock_db, email, otp="123456", expires_delta_minutes=5):
    mock_db.email_otps.insert_one(
        {
            "email": email,
            "otp": otp,
            "expires_at": datetime.now(timezone.utc)
            + timedelta(minutes=expires_delta_minutes),
        }
    )


def _seed_verified_otp_record(mock_db, email, verified_minutes_ago=1):
    mock_db.email_otps.insert_one(
        {
            "email": email,
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "verified": True,
            "verified_at": datetime.now(timezone.utc)
            - timedelta(minutes=verified_minutes_ago),
        }
    )


#---- Tests — complete signup with OTP ----


def test_complete_signup_requires_verified_otp(client, mock_db):
    response = client.post(
        "/api/auth/complete-signup",
        json={
            "email": "novalidation@example.com",
            "username": "otp_user_1",
            "password": "StrongPass@123",
        },
    )

    assert response.status_code == 403
    assert "Email not verified" in response.get_json()["error"]


def test_complete_signup_rejects_expired_verified_session(client, mock_db):
    _seed_verified_otp_record(mock_db, "expired@example.com", verified_minutes_ago=11)

    response = client.post(
        "/api/auth/complete-signup",
        json={
            "email": "expired@example.com",
            "username": "otp_user_2",
            "password": "StrongPass@123",
        },
    )

    assert response.status_code == 403
    assert "expired" in response.get_json()["error"].lower()


def test_verify_then_complete_signup_succeeds_within_window(client, mock_db):
    _seed_otp_record(mock_db, "fresh@example.com", otp="654321")

    verify_response = client.post(
        "/api/auth/verify-otp",
        json={"email": "fresh@example.com", "otp": "654321"},
    )
    assert verify_response.status_code == 200

    signup_response = client.post(
        "/api/auth/complete-signup",
        json={
            "email": "fresh@example.com",
            "username": "otp_user_3",
            "password": "StrongPass@123",
        },
    )

    assert signup_response.status_code == 201
    body = signup_response.get_json()
    assert "access_token" in body
    assert body["role"] == "user"
    assert mock_db.users.find_one({"email": "fresh@example.com"}) is not None


#---- Tests — set password with OTP ----


def test_set_password_reset_requires_verified_otp(client, mock_db):
    _seed_existing_user(mock_db, "resetuser@example.com", username="reset_user")

    response = client.post(
        "/api/auth/set-password",
        json={
            "email": "resetuser@example.com",
            "password": "NewPass@123",
            "purpose": "reset",
        },
    )

    assert response.status_code == 403
    assert "Email not verified" in response.get_json()["error"]


def test_set_password_reset_rejects_expired_verified_session(client, mock_db):
    _seed_existing_user(mock_db, "resetexpired@example.com", username="reset_expired")
    _seed_verified_otp_record(
        mock_db, "resetexpired@example.com", verified_minutes_ago=11
    )

    response = client.post(
        "/api/auth/set-password",
        json={
            "email": "resetexpired@example.com",
            "password": "NewPass@123",
            "purpose": "reset",
        },
    )

    assert response.status_code == 403
    assert "expired" in response.get_json()["error"].lower()


def test_verify_then_set_password_reset_succeeds_within_window(client, mock_db):
    _seed_existing_user(mock_db, "resetok@example.com", username="reset_ok")
    _seed_otp_record(mock_db, "resetok@example.com", otp="111222")

    verify_response = client.post(
        "/api/auth/verify-otp",
        json={"email": "resetok@example.com", "otp": "111222"},
    )
    assert verify_response.status_code == 200

    reset_response = client.post(
        "/api/auth/set-password",
        json={
            "email": "resetok@example.com",
            "password": "BrandNew@123",
            "purpose": "reset",
        },
    )

    assert reset_response.status_code == 200
    body = reset_response.get_json()
    assert "access_token" in body
    assert body["role"] == "user"
