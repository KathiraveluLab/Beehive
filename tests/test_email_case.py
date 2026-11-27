from datetime import datetime, timezone


def _seed_verified_otp(mock_db, email):
    mock_db.email_otps.insert_one(
        {"email": email, "verified": True, "verified_at": datetime.now(timezone.utc)}
    )


def test_signup_and_login_ignore_email_case(client, mock_db):
    _seed_verified_otp(mock_db, "bob@example.com")

    signup = client.post(
        "/api/auth/complete-signup",
        json={
            "email": "Bob@Example.com",
            "username": "bobby",
            "password": "StrongPass@123",
        },
    )
    assert signup.status_code == 201
    assert mock_db.users.find_one({"username": "bobby"})["email"] == "bob@example.com"

    login = client.post(
        "/api/auth/login",
        json={"username": "BOB@example.com", "password": "StrongPass@123"},
    )
    assert login.status_code == 200


def test_signup_rejects_email_differing_only_in_case(client, mock_db):
    _seed_verified_otp(mock_db, "bob@example.com")
    first = client.post(
        "/api/auth/complete-signup",
        json={"email": "bob@example.com", "username": "bobby", "password": "StrongPass@123"},
    )
    assert first.status_code == 201

    _seed_verified_otp(mock_db, "bob@example.com")
    second = client.post(
        "/api/auth/complete-signup",
        json={"email": "BOB@example.com", "username": "bobby2", "password": "StrongPass@123"},
    )
    assert second.status_code == 400
    assert mock_db.users.count_documents({}) == 1
