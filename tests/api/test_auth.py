import pytest
import mongomock
from unittest.mock import patch
import bcrypt
from datetime import datetime, timedelta, timezone


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client.beehive
    with patch("routes.auth.get_db", return_value=db):
        yield db


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


def test_request_otp_reset_success(client, mock_db):
    """POST /api/auth/request-otp"""
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw
    })

    response = client.post("/api/auth/request-otp", json={
        "email": "test@example.com",
        "purpose": "reset"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "OTP stored (failed to send email)" # since we are not actually sending emails in tests


def test_request_otp_reset_failure(client, mock_db):
    """POST /api/auth/request-otp - Not existing user"""

    response = client.post("/api/auth/request-otp", json={
        "email": "test1@example.com",
        "purpose": "reset"
    })

    assert response.status_code == 200 # security purposes
    data = response.get_json()
    assert data["message"] == "If account exists, OTP sent"

def test_request_otp_signup_success(client, mock_db):
    """POST /api/auth/request-otp"""
    
    response = client.post("/api/auth/request-otp", json={
        "email": "test@example.com",
        "purpose": "signup"
    })

    assert response.status_code == 200 
    data = response.get_json()
    assert data["message"] == "OTP stored (failed to send email)" # since we are not actually sending emails in tests


def test_request_otp_signup_failure(client, mock_db):
    """POST /api/auth/request-otp - Not existing user"""
    hashed_pw = bcrypt.hashpw(b"securepassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw
    })

    response = client.post("/api/auth/request-otp", json={
        "email": "test@example.com",
        "purpose": "signup"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email already registered"


def test_verify_otp_success(client, mock_db):
    """POST /api/auth/verify-otp"""
    email = "test@example.com"
    otp = "123456"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    mock_db.email_otps.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": expires_at
        })
    
    response = client.post("/api/auth/verify-otp", json={
        "email": "test@example.com",
        "otp": "123456",
    })

    assert response.status_code == 200 
    data = response.get_json()
    assert data["message"] == "OTP verified"


def test_request_otp_failure(client, mock_db):
    """POST /api/auth/request-otp - Not existing user"""

    response = client.post("/api/auth/verify-otp", json={
        "email": "test@example.com",
        "otp": "000000",
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid OTP"


def test_set_password_signup_success(client, mock_db):
    """POST /api/auth/set-password - Signup"""
    response = client.post("/api/auth/set-password", json={
        "email": "newuser@example.com",
        "password": "securepassword",
        "purpose": "signup"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "user"

    user = mock_db.users.find_one({"email": "newuser@example.com"})
    assert user is not None
    assert bcrypt.checkpw(b"securepassword", user["password"])


def test_set_password_signup_existing_user(client, mock_db):
    """POST /api/auth/set-password - Signup with existing user"""
    mock_db.users.insert_one({
        "email": "existing@example.com",
        "username": "existing",
        "password": b"hashed"
    })

    response = client.post("/api/auth/set-password", json={
        "email": "existing@example.com",
        "password": "securepassword",
        "purpose": "signup"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "User already exists"


def test_set_password_reset_success(client, mock_db):
    """POST /api/auth/set-password - Reset"""
    hashed_pw = bcrypt.hashpw(b"oldpassword", bcrypt.gensalt())
    mock_db.users.insert_one({
        "email": "test@example.com",
        "username": "testuser",
        "password": hashed_pw,
        "role": "user"
    })

    response = client.post("/api/auth/set-password", json={
        "email": "test@example.com",
        "password": "newsecurepassword",
        "purpose": "reset"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "user"

    user = mock_db.users.find_one({"email": "test@example.com"})
    assert bcrypt.checkpw(b"newsecurepassword", user["password"])


def test_set_password_reset_not_found(client, mock_db):
    """POST /api/auth/set-password - Reset for non-existent user"""
    response = client.post("/api/auth/set-password", json={
        "email": "ghost@example.com",
        "password": "newsecurepassword",
        "purpose": "reset"
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "User not found"
