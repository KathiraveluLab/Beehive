"""
Tests for authentication functionality.
"""

import json
from werkzeug.security import generate_password_hash
import io
import uuid
import bcrypt
from unittest.mock import patch, PropertyMock
import pytest
from OAuth.config import ALLOWED_EMAILS

def generate_unique_email():
    """Generate a unique email for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def test_register_new_user(client):
    """Test registering a new user."""
    data = {
        'username': f'user_{uuid.uuid4().hex[:8]}',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'email': generate_unique_email(),
        'firstname': 'Test',
        'lastname': 'User',
        'security_question': 'What is your favorite color?',
        'security_answer': 'blue'
    }
    response = client.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data

def test_login_success(client):
    """Test successful login."""
    # First register a user
    username = f'user_{uuid.uuid4().hex[:8]}'
    data = {
        'username': username,
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'email': generate_unique_email(),
        'firstname': 'Login',
        'lastname': 'Test',
        'security_question': 'What is your favorite color?',
        'security_answer': 'blue'
    }
    client.post('/register', data=data)
    
    # Then try to login
    login_data = {
        'username': username,
        'password': 'testpass123'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful!' in response.data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    data = {
        'username': 'nonexistent',
        'password': 'wrongpass'
    }
    response = client.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid credentials' in response.data

def test_logout(authenticated_client):
    """Test logout functionality."""
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_forgot_password(client, test_user):
    """Test password reset functionality."""
    # First try with correct security answer
    data = {
        'username': test_user['username'],
        'security_answer': test_user['security_answer'],
        'new_password': 'newpass123'
    }
    response = client.post('/forgot_password', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password reset successful!' in response.data

    # Try logging in with new password
    login_data = {
        'username': test_user['username'],
        'password': 'newpass123'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful!' in response.data

def test_forgot_password_wrong_answer(client, test_user):
    """Test password reset with wrong security answer."""
    data = {
        'username': test_user['username'],
        'security_answer': 'wrong_answer',
        'new_password': 'newpass123'
    }
    response = client.post('/forgot_password', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect security answer!' in response.data

def test_change_password(authenticated_client, test_user):
    """Test password change functionality."""
    # Hash the password and update it in the database
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw('testpass123'.encode('utf-8'), salt)
    from Database.userdatahandler import beehive_user_collection
    beehive_user_collection.update_one(
        {"username": test_user['username']},
        {"$set": {"password": hashed_password}}
    )

    data = {
        'current_password': 'testpass123',  # Original plain text password
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }
    response = authenticated_client.post('/change-password', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data

def test_change_username(authenticated_client, test_user):
    """Test username change functionality."""
    new_username = f'user_{uuid.uuid4().hex[:8]}'
    data = {
        'new_username': new_username
    }
    response = authenticated_client.post('/change-username', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username updated successfully!' in response.data

def test_change_email(authenticated_client, test_user):
    """Test email change functionality."""
    data = {
        'new_email': generate_unique_email()
    }
    response = authenticated_client.post('/change-email', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email updated successfully!' in response.data

def test_google_login_redirect(client):
    """Test Google login redirect."""
    response = client.get('/login/google')
    assert response.status_code == 302  # Redirect to Google OAuth
    assert 'accounts.google.com' in response.location

@patch('google.oauth2.id_token.verify_oauth2_token')
@patch('google_auth_oauthlib.flow.Flow.fetch_token')
def test_google_login_callback_admin(mock_fetch_token, mock_verify_token, client):
    """Test Google login callback for admin user."""
    mock_verify_token.return_value = {
        'sub': '123456789',
        'name': 'Test Admin',
        'email': ALLOWED_EMAILS[0]
    }
    mock_fetch_token.return_value = {'access_token': 'fake_token'}
    
    with client.session_transaction() as session:
        session['state'] = 'test_state'
    
    response = client.get('/admin/login/callback?state=test_state&code=fake_code', follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin' in response.data

@patch('google.oauth2.id_token.verify_oauth2_token')
@patch('google_auth_oauthlib.flow.Flow.fetch_token')
def test_google_login_callback_regular_user(mock_fetch_token, mock_verify_token, client):
    """Test Google login callback for regular user."""
    mock_verify_token.return_value = {
        'sub': '123456789',
        'name': 'Test User',
        'email': 'user@test.com'
    }
    mock_fetch_token.return_value = {'access_token': 'fake_token'}
    
    with client.session_transaction() as session:
        session['state'] = 'test_state'
    
    response = client.get('/login/google/callback?state=test_state&code=fake_code', follow_redirects=True)
    assert response.status_code == 200
    assert b'No account exists with this email' in response.data

def test_google_register(client):
    """Test Google registration page."""
    with client.session_transaction() as session:
        session['google_login_pending'] = True
        session['name'] = 'Test User'
        session['email'] = 'user@test.com'
        session['google_id'] = '123456789'
    
    response = client.get('/register/google')
    assert response.status_code == 200
    assert b'Complete Registration' in response.data

def test_google_register_submit(client):
    """Test submitting Google registration."""
    with client.session_transaction() as session:
        session['google_login_pending'] = True
        session['name'] = 'Test User'
        session['email'] = 'user@test.com'
        session['google_id'] = '123456789'
    
    data = {
        'username': 'testuser',
        'firstname': 'Test',
        'lastname': 'User',
        'security_question': 'What is your favorite color?',
        'security_answer': 'Blue'
    }
    
    response = client.post('/register/google', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data 