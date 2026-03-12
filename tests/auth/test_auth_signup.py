import pytest
import mongomock
from unittest.mock import patch
import bcrypt
from datetime import datetime, timedelta, timezone

def test_complete_signup_success(client, mock_db):
    """POST /api/auth/complete-signup"""
    response = client.post("/api/auth/complete-signup", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })

    user = mock_db.users.find_one({"email": "test@example.com"})

    assert response.status_code == 201
    data = response.get_json()
    assert user is not None
    assert user["username"] == "testuser"
    assert bcrypt.checkpw(b"testpassword", user["password"])
    assert "access_token" in data
    assert "role" in data
    assert data["role"] == "user"
