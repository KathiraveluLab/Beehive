import bcrypt
import pytest
from unittest.mock import patch

#---- Tests — complete signup ----


@pytest.mark.parametrize(
    "user_data, is_admin, expected_role",
    [
        (
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword",
            },
            False,
            "user",
        ),
        (
            {
                "username": "adminuser",
                "email": "admin@example.com",
                "password": "adminpassword",
            },
            True,
            "admin",
        ),
    ],
)
def test_complete_signup_success(client, mock_db, user_data, is_admin, expected_role):
    """POST /api/auth/complete-signup for user and admin roles."""
    with patch("routes.auth.is_admin_email", return_value=is_admin):
        response = client.post("/api/auth/complete-signup", json=user_data)

    assert response.status_code == 201
    data = response.get_json()
    user = mock_db.users.find_one({"email": user_data["email"]})
    assert user is not None
    assert user["username"] == user_data["username"]
    assert bcrypt.checkpw(user_data["password"].encode("utf-8"), user["password"])
    assert "access_token" in data
    assert "role" in data
    assert data["role"] == expected_role
