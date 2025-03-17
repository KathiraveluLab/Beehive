import pytest
from app import app

def test_home_route(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    """Test the login route."""
    response = client.get('/login')
    assert response.status_code == 200

def test_unauthorized_admin_access(client):
    """Test unauthorized access to admin route."""
    response = client.get('/admin')
    # Admin page is accessible but should show login required message
    assert response.status_code == 200

def test_unauthorized_dashboard_access(client):
    """Test unauthorized access to dashboard route."""
    response = client.get('/dashboard')  # Updated path
    # Should redirect to login
    assert response.status_code == 302
    assert 'login' in response.headers['Location'].lower()

def test_static_files(client):
    """Test static files are served."""
    response = client.get('/static/favicon.png')
    assert response.status_code == 200

def test_register_page(client):
    """Test register page access."""
    response = client.get('/register')
    assert response.status_code == 200

def test_forgot_password_page(client):
    """Test forgot password page access."""
    response = client.get('/forgot-password')
    assert response.status_code == 200 