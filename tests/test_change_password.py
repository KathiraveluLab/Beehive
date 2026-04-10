"""
Tests for the PATCH /api/auth/change-password endpoint.

Verifies that authenticated users can change their password by providing
their current password and a valid new password.
"""

import json
from unittest.mock import patch, MagicMock

import bcrypt
import pytest
from bson import ObjectId

#---- Helpers ----

USER_ID = str(ObjectId())
CURRENT_PASSWORD = "currentpassword123"
NEW_PASSWORD = "newpassword456"


def _hashed(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _make_token(app, user_id=USER_ID, role="user"):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        return create_access_token(user_id, role)


def _patch(client, payload, token):
    return client.patch(
        "/api/auth/change-password",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )


#---- Tests — authentication guard ----


def test_change_password_no_token(client):
    """Request without Authorization header must return 401."""
    resp = client.patch(
        "/api/auth/change-password",
        data=json.dumps(
            {"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD}
        ),
        content_type="application/json",
    )
    assert resp.status_code == 401


def test_change_password_invalid_token(client):
    """Request with a bad token must return 401."""
    resp = client.patch(
        "/api/auth/change-password",
        data=json.dumps(
            {"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD}
        ),
        content_type="application/json",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


#---- Tests — input validation ----


def test_change_password_missing_current_password(client, app):
    """Missing current_password field must return 400."""
    token = _make_token(app)
    resp = _patch(client, {"new_password": NEW_PASSWORD}, token)
    assert resp.status_code == 400
    assert "current_password" in resp.get_json().get("error", "").lower()


def test_change_password_missing_new_password(client, app):
    """Missing new_password field must return 400."""
    token = _make_token(app)
    resp = _patch(client, {"current_password": CURRENT_PASSWORD}, token)
    assert resp.status_code == 400
    assert "new_password" in resp.get_json().get("error", "").lower()


def test_change_password_new_password_too_short(client, app):
    """new_password shorter than 8 characters must return 400."""
    token = _make_token(app)
    resp = _patch(
        client, {"current_password": CURRENT_PASSWORD, "new_password": "short"}, token
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Password must be at least 8 characters"


#---- Tests — business logic ----


@patch("routes.auth.db")
def test_change_password_user_not_found(mock_db, client, app):
    """Return 404 when the user ID from the JWT does not exist in DB."""
    mock_db.users.find_one.return_value = None
    token = _make_token(app)
    resp = _patch(
        client,
        {"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        token,
    )
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "User not found"


@patch("routes.auth.db")
def test_change_password_no_stored_password(mock_db, client, app):
    """Return 400 when the user has no password (e.g., Google OAuth-only account)."""
    mock_db.users.find_one.return_value = {"_id": ObjectId(USER_ID), "password": None}
    token = _make_token(app)
    resp = _patch(
        client,
        {"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        token,
    )
    assert resp.status_code == 400
    assert "password not set" in resp.get_json()["error"].lower()


@patch("routes.auth.db")
def test_change_password_wrong_current_password(mock_db, client, app):
    """Return 401 when current_password does not match the stored hash."""
    mock_db.users.find_one.return_value = {
        "_id": ObjectId(USER_ID),
        "password": _hashed(CURRENT_PASSWORD),
    }
    token = _make_token(app)
    resp = _patch(
        client,
        {"current_password": "wrongpassword", "new_password": NEW_PASSWORD},
        token,
    )
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Current password is incorrect"


@patch("routes.auth.db")
def test_change_password_same_as_current(mock_db, client, app):
    """Return 400 when new_password is the same as the current password."""
    mock_db.users.find_one.return_value = {
        "_id": ObjectId(USER_ID),
        "password": _hashed(CURRENT_PASSWORD),
    }
    token = _make_token(app)
    resp = _patch(
        client,
        {"current_password": CURRENT_PASSWORD, "new_password": CURRENT_PASSWORD},
        token,
    )
    assert resp.status_code == 400
    assert "different" in resp.get_json()["error"].lower()


@patch("routes.auth.db")
def test_change_password_success(mock_db, client, app):
    """Successfully change password returns 200 and updates the DB."""
    mock_db.users.find_one.return_value = {
        "_id": ObjectId(USER_ID),
        "password": _hashed(CURRENT_PASSWORD),
    }
    token = _make_token(app)
    resp = _patch(
        client,
        {"current_password": CURRENT_PASSWORD, "new_password": NEW_PASSWORD},
        token,
    )
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Password updated successfully"
    mock_db.users.update_one.assert_called_once()

    # Verify the call targeted the right user
    call_filter = mock_db.users.update_one.call_args[0][0]
    assert call_filter == {"_id": ObjectId(USER_ID)}
