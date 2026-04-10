import bcrypt
import pytest

#---- Fixtures ----


@pytest.fixture
def created_user(mock_db):
    """Fixture to create a user in the mock database."""
    password = "securepassword"
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw,
    }
    mock_db.users.insert_one(user_data)
    return {
        "email": user_data["email"],
        "username": user_data["username"],
        "password": password,
    }


#---- Tests — successful login ----


@pytest.mark.parametrize("login_identifier_key", ["email", "username"])
def test_login_success(client, created_user, login_identifier_key):
    """
    POST /api/auth/login with valid credentials (email or username).
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": created_user[login_identifier_key],
            "password": created_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


#---- Tests — failed login ----


def test_login_invalid_credentials(client, created_user):
    """POST /api/auth/login - invalid credentials should return 401"""
    response = client.post(
        "/api/auth/login",
        json={"username": created_user["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.get_json()
    assert "access_token" not in data
