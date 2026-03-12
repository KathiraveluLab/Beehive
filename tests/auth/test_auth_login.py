import pytest
import mongomock
from unittest.mock import patch
import bcrypt
from datetime import datetime, timedelta, timezone

def test_login_success(client, mock_db):
    """
    POST /api/auth/login
    """
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw
    })

    response = client.post("/api/auth/login", json={
        "username": "test@example.com", # Works with email
        "password": "securepassword"
    })

    # 3. Assert the result
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_login_invalid_credentials(client, mock_db):
    """POST /api/auth/login - invalid credentials should return 401"""
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw
    })

    # 2. Make the API request
    response = client.post("/api/auth/login", json={
        "username": "test@example.com",
        "password": "wrongpassword"
    })

    # 3. Assert the result
    assert response.status_code == 401
    data = response.get_json()
    assert "access_token" not in data
