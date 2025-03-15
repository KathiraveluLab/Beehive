"""
This file contains shared pytest fixtures that can be used across multiple test files.
"""

import pytest
from app import app, create_user, get_user_by_username
import datetime

@pytest.fixture
def app():
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "beehive",
        "SERVER_NAME": "localhost"
    })
    yield app

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def app_context():
    """Create an application context for testing."""
    with app.app_context():
        yield 

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['username'] = test_user['username']
    return client

@pytest.fixture
def test_user(client):
    """Create a test user for authentication tests."""
    user_data = {
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com',
        'firstname': 'Test',
        'lastname': 'User',
        'security_question': 'What is your favorite color?',
        'security_answer': 'blue',
        'accountcreatedtime': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }
    
    # Only create user if it doesn't exist
    if not get_user_by_username('testuser'):
        create_user(**user_data)
    
    return user_data
