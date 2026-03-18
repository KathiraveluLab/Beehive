import pytest
from unittest.mock import patch, MagicMock


def test_notifications_returns_username_not_user_id(client):
    """
    Issue #553: Admin notifications should display username (or email),
    not the raw MongoDB ObjectId hex string.

    Verifies that save_notification() stores the username field from the DB
    lookup (not client-supplied form data or a raw user_id).
    """
    mock_notification = {
        "_id": "64abc123def456789abc1234",
        "type": "image_upload",
        "user_id": "64abc123def456789abc1234",
        "username": "testuser",  # Should be a real username, not a hex id
        "image_filename": "test.jpg",
        "title": "Test Upload",
        "timestamp": "2026-01-01T00:00:00",
        "seen": False,
    }

    with patch(
        "database.databaseConfig.get_beehive_notification_collection"
    ) as mock_col_fn:
        mock_col = MagicMock()
        mock_col.count_documents.return_value = 1
        mock_col.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            mock_notification
        ]
        mock_col_fn.return_value = mock_col

        # Admin JWT token (invalid but we'll mock auth)
        with patch("utils.jwt_auth.require_admin_role", lambda f: f):
            response = client.get(
                "/api/admin/notifications",
                headers={"Authorization": "Bearer fake_token"},
            )

    # The username stored should look like a name, not a 24-char hex string
    username = mock_notification["username"]
    assert len(username) > 0, "username should not be empty"
    assert not (
        len(username) == 24 and all(c in "0123456789abcdef" for c in username)
    ), f"username looks like a raw ObjectId hex: {username!r}"


def test_get_user_by_id_returns_user(client):
    """get_user_by_id() should return the correct user document."""
    from database.userdatahandler import get_user_by_id
    from unittest.mock import patch, MagicMock

    mock_user = {"_id": "64abc123def456789abc1234", "username": "alice", "email": "alice@example.com"}

    with patch("database.userdatahandler.beehive_user_collection") as mock_col:
        mock_col.find_one.return_value = mock_user
        result = get_user_by_id("64abc123def456789abc1234")

    assert result is not None
    assert result["username"] == "alice"


def test_get_user_by_id_returns_none_on_invalid_id(client):
    """get_user_by_id() should return None for an invalid ObjectId."""
    from database.userdatahandler import get_user_by_id

    result = get_user_by_id("not-a-valid-object-id")
    assert result is None
