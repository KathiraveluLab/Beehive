"""Tests for account lockout after repeated failed login attempts."""

import pytest
import bcrypt
from datetime import datetime, timezone
from bson import ObjectId
from database.userdatahandler import (
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    get_lock_status,
    increment_failed_attempts,
    reset_failed_attempts,
    unlock_account,
)

#---- Helpers ----

PASSWORD = "testpassword1"


def _insert_user(mock_db, username="lockuser", password=PASSWORD, role="user"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    result = mock_db.users.insert_one(
        {
            "username": username,
            "email": f"{username}@test.com",
            "password": hashed,
            "role": role,
            "created_at": datetime.now(timezone.utc),
            "last_active": datetime.now(timezone.utc),
        }
    )
    return result.inserted_id


def _login(client, username, password=PASSWORD):
    return client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )


def _admin_token(app, mock_db):
    uid = _insert_user(mock_db, username="adminuser", role="admin")
    with app.app_context():
        from utils.jwt_auth import create_access_token

        return create_access_token(str(uid), "admin")


#---- Unit tests — DB helpers ----


def test_fresh_user_not_locked(mock_db):
    uid = _insert_user(mock_db, "freshuser")
    status = get_lock_status(str(uid))
    assert status["is_locked"] is False
    assert status["failed_attempts"] == 0


def test_increment_tracks_count(mock_db):
    uid = _insert_user(mock_db, "countuser")
    assert increment_failed_attempts(str(uid)) == 1
    assert increment_failed_attempts(str(uid)) == 2
    assert get_lock_status(str(uid))["failed_attempts"] == 2


def test_account_locks_at_threshold(mock_db):
    uid = _insert_user(mock_db, "lockthreshold")
    for _ in range(MAX_FAILED_ATTEMPTS):
        increment_failed_attempts(str(uid))
    status = get_lock_status(str(uid))
    assert status["is_locked"] is True
    assert status["remaining_seconds"] > 0


def test_reset_clears_counter_and_lock(mock_db):
    uid = _insert_user(mock_db, "resetuser")
    for _ in range(MAX_FAILED_ATTEMPTS):
        increment_failed_attempts(str(uid))
    assert get_lock_status(str(uid))["is_locked"] is True
    reset_failed_attempts(str(uid))
    status = get_lock_status(str(uid))
    assert status["is_locked"] is False
    assert status["failed_attempts"] == 0


def test_unlock_account_clears_lock(mock_db):
    uid = _insert_user(mock_db, "unlockuser")
    for _ in range(MAX_FAILED_ATTEMPTS):
        increment_failed_attempts(str(uid))
    assert get_lock_status(str(uid))["is_locked"] is True
    assert unlock_account(str(uid)) is True
    assert get_lock_status(str(uid))["is_locked"] is False


def test_unlock_nonexistent_user_returns_false():
    assert unlock_account(str(ObjectId())) is False


def test_get_lock_status_invalid_id():
    status = get_lock_status("not-an-objectid")
    assert status["is_locked"] is False


#---- Integration tests — login endpoint ----


def test_wrong_password_shows_attempts_remaining(client, mock_db):
    _insert_user(mock_db, "warnuser")
    res = _login(client, "warnuser", "wrongpassword")
    assert res.status_code == 401
    assert "remaining" in res.get_json()["error"].lower()


def test_counter_decrements_warning_on_each_failure(client, mock_db):
    _insert_user(mock_db, "countdownuser")
    for i in range(1, MAX_FAILED_ATTEMPTS):
        res = _login(client, "countdownuser", "wrong")
        assert res.status_code == 401
        assert str(MAX_FAILED_ATTEMPTS - i) in res.get_json()["error"]


def test_fifth_failure_returns_429(client, mock_db):
    _insert_user(mock_db, "lockme")
    for _ in range(MAX_FAILED_ATTEMPTS):
        res = _login(client, "lockme", "wrong")
    assert res.status_code == 429
    data = res.get_json()
    assert data["locked"] is True
    assert "remaining_seconds" in data


def test_locked_account_blocks_correct_password(client, mock_db):
    _insert_user(mock_db, "blockeduser", password="correctpass")
    for _ in range(MAX_FAILED_ATTEMPTS):
        _login(client, "blockeduser", "wrong")
    res = _login(client, "blockeduser", "correctpass")
    assert res.status_code == 429
    assert res.get_json()["locked"] is True


def test_successful_login_resets_failed_counter(client, mock_db):
    uid = _insert_user(mock_db, "resetonlogin", password="goodpass")
    _login(client, "resetonlogin", "wrong")
    _login(client, "resetonlogin", "wrong")
    assert get_lock_status(str(uid))["failed_attempts"] == 2
    res = _login(client, "resetonlogin", "goodpass")
    assert res.status_code == 200
    assert get_lock_status(str(uid))["failed_attempts"] == 0


def test_lockout_response_includes_remaining_seconds(client, mock_db):
    _insert_user(mock_db, "timedlock")
    for _ in range(MAX_FAILED_ATTEMPTS):
        _login(client, "timedlock", "wrong")
    res = _login(client, "timedlock", "wrong")
    data = res.get_json()
    assert 0 < data["remaining_seconds"] <= LOCKOUT_DURATION_MINUTES * 60


#---- Admin unlock endpoint ----


def test_admin_can_unlock_locked_account(client, app, mock_db):
    uid = _insert_user(mock_db, "targetlock")
    for _ in range(MAX_FAILED_ATTEMPTS):
        increment_failed_attempts(str(uid))
    assert get_lock_status(str(uid))["is_locked"] is True

    token = _admin_token(app, mock_db)
    res = client.post(
        f"/api/admin/users/{uid}/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert get_lock_status(str(uid))["is_locked"] is False


def test_admin_unlock_nonexistent_user_returns_404(client, app, mock_db):
    token = _admin_token(app, mock_db)
    res = client.post(
        f"/api/admin/users/{ObjectId()}/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404


def test_non_admin_cannot_unlock(client, app, mock_db):
    target_uid = _insert_user(mock_db, "targetuser2")
    for _ in range(MAX_FAILED_ATTEMPTS):
        increment_failed_attempts(str(target_uid))

    regular_uid = _insert_user(mock_db, "regularuser3")
    with app.app_context():
        from utils.jwt_auth import create_access_token

        user_token = create_access_token(str(regular_uid), "user")

    res = client.post(
        f"/api/admin/users/{target_uid}/unlock",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 403
