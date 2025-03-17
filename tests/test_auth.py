"""
This file contains tests for authentication-related functionality.
"""

import bcrypt
from Database.userdatahandler import get_user_by_username

def test_register_success(client):
    """Test successful registration."""
    response = client.post("/register", data={
        "firstname": "Test",
        "lastname": "User",
        "email": "test123@gmail.com",
        "username": "testuser123",
        "password": "password123",
        "confirm_password": "password123",
        "security_question": "What is your favorite book?",
        "security_answer": "1984"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration successful!" in response.data

    # Check if user was added to the database
    user = get_user_by_username("testuser123")
    assert user is not None
    assert user["mail_id"] == "test123@gmail.com"

def test_register_password_mismatch(client):
    """Test registration failure due to mismatched passwords."""
    response = client.post("/register", data={
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "username": "testuser123",
        "password": "password123",
        "confirm_password": "wrongpassword",
        "security_question": "What is your favorite book?",
        "security_answer": "1984"
    })

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post("/login", data={
        "username": test_user["username"],
        "password": "wrongpassword"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_logout(authenticated_client):
    """Test logout functionality."""
    response = authenticated_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out" in response.data

def test_forgot_password(client, test_user):
    """Test forgot password functionality."""
    response = client.post("/forgot-password", data={
        "username": test_user["username"],
        "security_question": test_user["security_question"],
        "security_answer": test_user["security_answer"],
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Password updated successfully" in response.data

def test_forgot_password_wrong_answer(client, test_user):
    """Test forgot password with wrong security answer."""
    response = client.post("/forgot-password", data={
        "username": test_user["username"],
        "security_question": test_user["security_question"],
        "security_answer": "wrong_answer",
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Incorrect security answer" in response.data

def test_change_password(authenticated_client, test_user):
    """Test password change functionality."""
    response = authenticated_client.post("/change-password", data={
        "current_password": test_user["password"],
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Password updated successfully" in response.data

def test_change_username(authenticated_client, test_user):
    """Test username change functionality."""
    new_username = "newusername123"
    response = authenticated_client.post("/change-username", data={
        "new_username": new_username
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Username updated successfully" in response.data

def test_change_email(authenticated_client, test_user):
    """Test email change functionality."""
    new_email = "newemail@example.com"
    response = authenticated_client.post("/change-email", data={
        "new_email": new_email
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Email updated successfully" in response.data

# Google OAuth Tests
def test_google_login_redirect(client):
    """Test Google login redirect."""
    response = client.get("/login/google")
    assert response.status_code == 302
    assert "accounts.google.com" in response.location

def test_google_login_callback_admin(client, monkeypatch):
    """Test Google login callback for admin user."""
    # Mock the Google OAuth response
    def mock_google_oauth():
        return {
            "email": "admin@example.com",
            "given_name": "Admin",
            "family_name": "User",
            "sub": "123456789"  # This is the Google ID
        }
    monkeypatch.setattr("app.google_oauth.get_user_info", mock_google_oauth)
    
    with client.session_transaction() as session:
        session['google_id'] = "123456789"
        session['name'] = "Admin User"
        session['email'] = "admin@example.com"
    
    response = client.get("/admin/login/callback", follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome Admin" in response.data

def test_google_login_callback_regular_user(client, monkeypatch):
    """Test Google login callback for regular user."""
    # Mock the Google OAuth response
    def mock_google_oauth():
        return {
            "email": "user@example.com",
            "given_name": "Test",
            "family_name": "User",
            "sub": "987654321"  # This is the Google ID
        }
    monkeypatch.setattr("app.google_oauth.get_user_info", mock_google_oauth)
    
    with client.session_transaction() as session:
        session['google_id'] = "987654321"
        session['name'] = "Test User"
        session['email'] = "user@example.com"
    
    response = client.get("/admin/login/callback", follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_google_register(client):
    """Test Google registration page."""
    with client.session_transaction() as session:
        session['google_id'] = "987654321"
        session['name'] = "Test User"
        session['email'] = "newuser@example.com"
    
    response = client.get("/register/google", follow_redirects=True)
    assert response.status_code == 200
    assert b"Complete Registration" in response.data

def test_google_register_submit(client):
    """Test Google registration submission."""
    with client.session_transaction() as session:
        session['google_id'] = "987654321"
        session['name'] = "Test User"
        session['email'] = "newuser@example.com"
    
    response = client.post("/register/google", data={
        "firstname": "New",
        "lastname": "User",
        "username": "newgoogleuser"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Registration successful" in response.data



