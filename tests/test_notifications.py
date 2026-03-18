import pytest
from unittest.mock import patch, MagicMock
import io
from bson import ObjectId


def test_upload_images_stores_correct_username_in_notification(client):
    """
    Issue #553: Verify that uploading an image stores the actual username
    in the notification document, retrieved from the user database.
    """
    mock_user = {
        "_id": ObjectId("64abc123def456789abc1234"),
        "username": "real_test_user",
        "email": "test@example.com"
    }

    # Mock dependencies to avoid filesystem and MIME detection issues
    with patch("app.get_user_by_id") as mock_get_user, \
         patch("app.save_notification") as mock_save_notif, \
         patch("app.save_image"), \
         patch("app.os.makedirs"), \
         patch("werkzeug.datastructures.FileStorage.save"), \
         patch("app.MAGIC") as mock_magic:
        
        mock_get_user.return_value = mock_user
        # Mock MIME detection to return an allowed type
        mock_magic.from_buffer.return_value = "image/jpeg"
        
        # Call the upload endpoint with mocked auth
        with patch("utils.jwt_auth.verify_jwt") as mock_verify:
            mock_verify.return_value = {"sub": str(mock_user["_id"]), "role": "user"}
            
            # Form data for upload
            test_data = {
                "title": "Test Title",
                "sentiment": "positive",
                "description": "Test Description",
                "files": [(io.BytesIO(b"dummy image data"), "test.jpg")]
            }

            response = client.post(
                "/api/user/upload",
                data=test_data,
                headers={"Authorization": "Bearer fake_token"},
                content_type="multipart/form-data"
            )

    assert response.status_code == 200
    
    # Critical assertion: verify save_notification was called with the username, not hex ID
    args, kwargs = mock_save_notif.call_args
    assert args[1] == "real_test_user", f"Expected username 'real_test_user', got {args[1]!r}"


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
    """get_user_by_id() should return None for an invalid ObjectId or error."""
    from database.userdatahandler import get_user_by_id

    result = get_user_by_id("not-a-valid-object-id")
    assert result is None
