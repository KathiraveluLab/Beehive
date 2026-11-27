"""A password change must end every session that was opened with the old password."""
import json
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from bson import ObjectId

OLD_PASSWORD = "oldpassword123"
NEW_PASSWORD = "newpassword456"
SECRET = "test-secret-key-minimum-32-chars-long-for-pytest"


def _make_user(db, password=OLD_PASSWORD, **extra):
    doc = {
        "email": "alice@example.com",
        "username": "alice",
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
        "role": "user",
    }
    doc.update(extra)
    return str(db.users.insert_one(doc).inserted_id)


def _token(app, user_id, role="user", issued_at=None):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        token = create_access_token(user_id, role)
    if issued_at is None:
        return token
    claims = jwt.decode(token, SECRET, algorithms=["HS256"])
    claims["iat"] = int(issued_at.timestamp())
    claims["exp"] = int((issued_at + timedelta(hours=24)).timestamp())
    return jwt.encode(claims, SECRET, algorithm="HS256")


def _me(client, token):
    return client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})


def _change_password(client, token):
    return client.patch(
        "/api/auth/change-password",
        data=json.dumps({"current_password": OLD_PASSWORD, "new_password": NEW_PASSWORD}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )


def test_old_token_is_rejected_after_password_change(client, app, mock_db):
    user_id = _make_user(mock_db)
    stolen = _token(app, user_id, issued_at=datetime.now(timezone.utc) - timedelta(hours=3))
    mine = _token(app, user_id, issued_at=datetime.now(timezone.utc) - timedelta(hours=1))
    assert _me(client, stolen).status_code == 200

    assert _change_password(client, mine).status_code == 200

    assert _me(client, stolen).status_code == 401
    assert _me(client, mine).status_code == 401


def test_change_password_returns_a_token_that_keeps_working(client, app, mock_db):
    user_id = _make_user(mock_db)
    old = _token(app, user_id, issued_at=datetime.now(timezone.utc) - timedelta(hours=1))

    resp = _change_password(client, old)

    assert resp.status_code == 200
    fresh = resp.get_json()["access_token"]
    assert _me(client, fresh).status_code == 200


def test_password_reset_ends_old_sessions(client, app, mock_db):
    user_id = _make_user(mock_db)
    stolen = _token(app, user_id, issued_at=datetime.now(timezone.utc) - timedelta(hours=3))
    mock_db.email_otps.insert_one(
        {"email": "alice@example.com", "verified": True, "created_at": datetime.now(timezone.utc)}
    )
    from unittest.mock import patch

    with patch("routes.auth._validate_otp_verification", return_value=None):
        resp = client.post(
            "/api/auth/set-password",
            data=json.dumps({"email": "alice@example.com", "password": NEW_PASSWORD, "purpose": "reset"}),
            content_type="application/json",
        )
    assert resp.status_code == 200

    assert _me(client, stolen).status_code == 401
    assert _me(client, resp.get_json()["access_token"]).status_code == 200


def test_token_issued_after_the_change_is_accepted(client, app, mock_db):
    changed = datetime.now(timezone.utc) - timedelta(hours=2)
    user_id = _make_user(mock_db, password_changed_at=changed)
    after = _token(app, user_id, issued_at=changed + timedelta(minutes=5))
    before = _token(app, user_id, issued_at=changed - timedelta(minutes=5))

    assert _me(client, after).status_code == 200
    assert _me(client, before).status_code == 401


def test_token_minted_in_the_same_second_as_the_change_is_accepted(client, app, mock_db):
    now = datetime.now(timezone.utc)
    user_id = _make_user(mock_db, password_changed_at=now)
    token = _token(app, user_id, issued_at=now.replace(microsecond=0))

    assert _me(client, token).status_code == 200


def test_admin_routes_also_reject_tokens_from_before_the_change(client, app, mock_db):
    admin_id = _make_user(
        mock_db,
        role="admin",
        password_changed_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    old = _token(app, admin_id, role="admin", issued_at=datetime.now(timezone.utc) - timedelta(hours=1))
    new = _token(app, admin_id, role="admin")

    assert client.get("/api/admin/users", headers={"Authorization": f"Bearer {old}"}).status_code == 401
    assert client.get("/api/admin/users", headers={"Authorization": f"Bearer {new}"}).status_code == 200


def test_users_who_never_changed_their_password_are_unaffected(client, app, mock_db):
    user_id = _make_user(mock_db)

    assert _me(client, _token(app, user_id)).status_code == 200


def test_token_for_an_unknown_user_id_still_decodes(client, app):
    """Tokens minted for ids with no user document (as other tests do) are not rejected here."""
    token = _token(app, "mock_admin_id", role="admin")

    assert client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"}).status_code != 401
