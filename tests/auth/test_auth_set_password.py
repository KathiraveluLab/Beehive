"""
Tests for the /api/auth/set-password endpoint.

Validates that the `purpose` field is correctly extracted,
validated, and routed to the signup or reset logic.
"""

import json
from unittest.mock import patch

import bcrypt
from bson.objectid import ObjectId

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _post_set_password(client, payload):
    """Helper to POST JSON to /api/auth/set-password."""
    return client.post(
        "/api/auth/set-password",
        data=json.dumps(payload),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# Tests — missing / invalid fields
# ---------------------------------------------------------------------------


def test_set_password_missing_purpose(client):
    """Endpoint must return 400 when purpose is missing (was a NameError crash)."""
    resp = _post_set_password(
        client,
        {
            "email": "user@example.com",
            "password": "securepassword123",
            # purpose intentionally omitted
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "purpose is required"


def test_set_password_invalid_purpose(client):
    """Endpoint must reject unknown purpose values."""
    resp = _post_set_password(
        client,
        {
            "email": "user@example.com",
            "password": "securepassword123",
            "purpose": "delete",
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Invalid purpose. Must be 'signup' or 'reset'."


def test_set_password_missing_email(client):
    """Endpoint must return 400 when email is missing."""
    resp = _post_set_password(
        client,
        {
            "password": "securepassword123",
            "purpose": "reset",
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "email is required"


def test_set_password_missing_password(client):
    """Endpoint must return 400 when password is missing."""
    resp = _post_set_password(
        client,
        {
            "email": "user@example.com",
            "purpose": "reset",
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "field is required"


def test_set_password_short_password(client):
    """Password shorter than 8 characters must be rejected."""
    resp = _post_set_password(
        client,
        {
            "email": "user@example.com",
            "password": "short",
            "purpose": "reset",
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Password must be at least 8 characters"


# ---------------------------------------------------------------------------
# Tests — reset purpose
# ---------------------------------------------------------------------------


@patch("routes.auth.create_access_token", return_value="mock-jwt-token")
def test_set_password_reset_success(mock_token, mock_db, client):
    """Successful password reset returns a new access token."""
    user = {
        "_id": ObjectId(),
        "email": "user@example.com",
        "role": "user",
        "password": bcrypt.hashpw(b"oldpassword", bcrypt.gensalt()),
    }
    mock_db.users.insert_one(user)

    resp = _post_set_password(
        client,
        {
            "email": "user@example.com",
            "password": "newsecurepassword",
            "purpose": "reset",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["access_token"] == "mock-jwt-token"
    assert data["role"] == "user"

    updated_user = mock_db.users.find_one({"email": "user@example.com"})
    assert bcrypt.checkpw(b"newsecurepassword", updated_user["password"])


def test_set_password_reset_user_not_found(mock_db, client):
    """Reset must return 404 if user does not exist."""
    resp = _post_set_password(
        client,
        {
            "email": "ghost@example.com",
            "password": "newsecurepassword",
            "purpose": "reset",
        },
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"] == "User not found"


# ---------------------------------------------------------------------------
# Tests — signup purpose
# ---------------------------------------------------------------------------


@patch("routes.auth.is_admin_email", return_value=False)
@patch("routes.auth.create_access_token", return_value="mock-jwt-token")
def test_set_password_signup_success(mock_admin, mock_token, mock_db, client):
    """Successful signup via set-password returns a new access token."""
    resp = _post_set_password(
        client,
        {
            "email": "newuser@example.com",
            "password": "newsecurepassword",
            "purpose": "signup",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["access_token"] == "mock-jwt-token"
    assert data["role"] == "user"

    # Verify user was created in DB
    created_user = mock_db.users.find_one({"email": "newuser@example.com"})
    assert created_user is not None
    assert created_user["role"] == "user"
    assert bcrypt.checkpw(b"newsecurepassword", created_user["password"])


def test_set_password_signup_duplicate_email(mock_db, client):
    """Signup must return 400 if user already exists."""
    mock_db.users.insert_one({"email": "dup@example.com", "role": "user"})

    resp = _post_set_password(
        client,
        {
            "email": "dup@example.com",
            "password": "newsecurepassword",
            "purpose": "signup",
        },
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "User already exists"
