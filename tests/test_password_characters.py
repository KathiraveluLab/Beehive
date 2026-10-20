import datetime

import bcrypt
import pytest
from bson import ObjectId

from utils.jwt_auth import create_access_token

# Words that contain a MongoDB operator name. They are fine in a password, which is only hashed.
PASSWORDS = [
    "mysecret$info1",
    "hello$orange1",
    "p@ss$setX1",
    "Pa$$word1",
    "x$gt$lt$ne$in$or",
]


def _verify_email(mock_db, email):
    mock_db.email_otps.insert_one(
        {
            "email": email,
            "verified": True,
            "verified_at": datetime.datetime.now(datetime.timezone.utc),
        }
    )


@pytest.mark.parametrize("password", PASSWORDS)
def test_signup_accepts_passwords_with_operator_like_text(client, mock_db, password):
    _verify_email(mock_db, "alice@example.com")

    response = client.post(
        "/api/auth/complete-signup",
        json={"email": "alice@example.com", "username": "alice", "password": password},
    )

    assert response.status_code == 201
    stored = mock_db.users.find_one({"email": "alice@example.com"})
    assert bcrypt.checkpw(password.encode(), stored["password"])


@pytest.mark.parametrize("password", PASSWORDS)
def test_login_accepts_passwords_with_operator_like_text(client, mock_db, password):
    mock_db.users.insert_one(
        {
            "email": "alice@example.com",
            "username": "alice",
            "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
            "role": "user",
        }
    )

    response = client.post(
        "/api/auth/login", json={"username": "alice", "password": password}
    )

    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_set_password_accepts_operator_like_text(client, mock_db):
    _verify_email(mock_db, "bob@example.com")

    response = client.post(
        "/api/auth/set-password",
        json={
            "email": "bob@example.com",
            "password": "mysecret$info1",
            "purpose": "signup",
        },
    )

    assert response.status_code == 200


def test_change_password_accepts_operator_like_text(client, app, mock_db):
    user_id = mock_db.users.insert_one(
        {
            "email": "alice@example.com",
            "username": "alice",
            "password": bcrypt.hashpw(b"old$orpassword1", bcrypt.gensalt()),
            "role": "user",
        }
    ).inserted_id
    with app.app_context():
        token = create_access_token(user_id=str(user_id), role="user")

    response = client.patch(
        "/api/auth/change-password",
        json={"current_password": "old$orpassword1", "new_password": "new$inpassword1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    stored = mock_db.users.find_one({"_id": user_id})
    assert bcrypt.checkpw(b"new$inpassword1", stored["password"])


def test_other_fields_still_reject_operator_text(client, mock_db):
    _verify_email(mock_db, "alice@example.com")

    response = client.post(
        "/api/auth/complete-signup",
        json={
            "email": "alice@example.com",
            "username": "al$ne",
            "password": "plainpassword1",
        },
    )

    assert response.status_code == 400
    assert mock_db.users.count_documents({}) == 0
