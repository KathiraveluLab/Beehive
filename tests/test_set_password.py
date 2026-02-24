"""
Tests for the /api/auth/set-password endpoint.

Validates that the `purpose` field is correctly extracted,
validated, and routed to the signup or reset logic.
"""
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest


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
    resp = _post_set_password(client, {
        "email": "user@example.com",
        "password": "securepassword123",
        # purpose intentionally omitted
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "purpose is required"


def test_set_password_invalid_purpose(client):
    """Endpoint must reject unknown purpose values."""
    resp = _post_set_password(client, {
        "email": "user@example.com",
        "password": "securepassword123",
        "purpose": "delete",
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert "purpose" in data["error"].lower() or "invalid" in data["error"].lower()


def test_set_password_missing_email(client):
    """Endpoint must return 400 when email is missing."""
    resp = _post_set_password(client, {
        "password": "securepassword123",
        "purpose": "reset",
    })
    assert resp.status_code == 400


def test_set_password_missing_password(client):
    """Endpoint must return 400 when password is missing."""
    resp = _post_set_password(client, {
        "email": "user@example.com",
        "purpose": "reset",
    })
    assert resp.status_code == 400


def test_set_password_short_password(client):
    """Password shorter than 8 characters must be rejected."""
    resp = _post_set_password(client, {
        "email": "user@example.com",
        "password": "short",
        "purpose": "reset",
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert "8 characters" in data["error"]


# ---------------------------------------------------------------------------
# Tests — reset purpose
# ---------------------------------------------------------------------------


@patch("routes.auth.db")
@patch("routes.auth.create_access_token", return_value="mock-jwt-token")
def test_set_password_reset_success(mock_token, mock_db, client):
    """Successful password reset returns a new access token."""
    mock_db.users.find_one.return_value = {
        "_id": "abc123",
        "email": "user@example.com",
        "role": "user",
    }

    resp = _post_set_password(client, {
        "email": "user@example.com",
        "password": "newsecurepassword",
        "purpose": "reset",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["access_token"] == "mock-jwt-token"
    assert data["role"] == "user"
    mock_db.users.update_one.assert_called_once()


@patch("routes.auth.db")
def test_set_password_reset_user_not_found(mock_db, client):
    """Reset must return 404 if user does not exist."""
    mock_db.users.find_one.return_value = None

    resp = _post_set_password(client, {
        "email": "ghost@example.com",
        "password": "newsecurepassword",
        "purpose": "reset",
    })
    assert resp.status_code == 404
    data = resp.get_json()
    assert "not found" in data["error"].lower()


# ---------------------------------------------------------------------------
# Tests — signup purpose
# ---------------------------------------------------------------------------


@patch("routes.auth.is_admin_email", return_value=False)
@patch("routes.auth.db")
@patch("routes.auth.create_access_token", return_value="mock-jwt-token")
def test_set_password_signup_success(mock_admin, mock_db, mock_token, client):
    """Successful signup via set-password returns a new access token."""
    mock_db.users.find_one.return_value = None  # no existing user
    mock_db.users.insert_one.return_value = MagicMock(inserted_id="new-id-123")

    resp = _post_set_password(client, {
        "email": "newuser@example.com",
        "password": "newsecurepassword",
        "purpose": "signup",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["access_token"] == "mock-jwt-token"
    assert data["role"] == "user"


@patch("routes.auth.db")
def test_set_password_signup_duplicate_email(mock_db, client):
    """Signup must return 400 if user already exists."""
    mock_db.users.find_one.return_value = {"_id": "exists", "email": "dup@example.com"}

    resp = _post_set_password(client, {
        "email": "dup@example.com",
        "password": "newsecurepassword",
        "purpose": "signup",
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert "already exists" in data["error"].lower()
