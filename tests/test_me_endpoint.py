"""
Tests for GET /api/auth/me endpoint.

Verifies that authenticated users can retrieve their own profile information.
"""

from datetime import datetime, timezone

import pytest
from bson import ObjectId

#---- Helpers ----

USER_ID = str(ObjectId())


def _make_token(app, user_id=USER_ID, role="user"):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        return create_access_token(user_id, role)


def _get(client, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.get("/api/auth/me", headers=headers)


def _insert_user(mock_db, user_id=USER_ID, provider="local", has_password=True):
    import bcrypt

    user = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "provider": provider,
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
    }
    if has_password:
        user["password"] = bcrypt.hashpw(b"password123", bcrypt.gensalt())
    mock_db.users.insert_one(user)


#---- Tests — authentication guard ----


def test_me_no_token(client):
    """Request without Authorization header must return 401."""
    resp = _get(client)
    assert resp.status_code == 401


def test_me_invalid_token(client):
    """Request with a bogus token must return 401."""
    resp = _get(client, token="not.a.valid.token")
    assert resp.status_code == 401


#---- Tests — successful profile retrieval ----


def test_me_returns_profile(client, app, mock_db):
    """Authenticated user receives their profile data."""
    _insert_user(mock_db)
    token = _make_token(app)
    resp = _get(client, token)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["provider"] == "local"
    assert data["role"] == "user"
    assert data["has_password"] is True
    assert data["created_at"] is not None


def test_me_password_not_exposed(client, app, mock_db):
    """The hashed password must never appear in the response."""
    _insert_user(mock_db)
    token = _make_token(app)
    resp = _get(client, token)
    assert "password" not in resp.get_json()


def test_me_google_user(client, app, mock_db):
    """Google OAuth users have provider='google' and has_password=False."""
    _insert_user(mock_db, provider="google", has_password=False)
    token = _make_token(app)
    resp = _get(client, token)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["provider"] == "google"
    assert data["has_password"] is False


def test_me_user_not_found(client, app):
    """Token referencing a non-existent user returns 404."""
    token = _make_token(app, user_id=str(ObjectId()))
    resp = _get(client, token)
    assert resp.status_code == 404
