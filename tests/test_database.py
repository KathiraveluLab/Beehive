import pytest
from datetime import datetime
from pymongo import MongoClient
from Database.DatabaseConfig import DatabaseConfig
from Database.userdatahandler import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    is_username_available,
    is_email_available,
    create_google_user
)

def test_create_user(test_db):
    """Test user creation in database."""
    now = datetime.now()
    
    # First check username and email availability
    assert is_username_available("testuser") == True
    assert is_email_available("test@example.com") == True
    
    create_user(
        firstname="Test",
        lastname="User",
        email="test@example.com",
        username="testuser",
        password="testpass123",
        security_question="What is your favorite color?",
        security_answer="blue",
        accountcreatedtime=now
    )
    
    # Verify user was created
    user = get_user_by_email("test@example.com")
    assert user is not None
    assert user["first_name"] == "Test"
    assert user["last_name"] == "User"
    assert user["username"] == "testuser"
    assert user["mail_id"] == "test@example.com"

def test_create_google_user(test_db):
    """Test Google user creation in database."""
    now = datetime.now().isoformat()
    
    # First check username and email availability
    assert is_username_available("googleuser") == True
    assert is_email_available("google@example.com") == True
    
    create_google_user(
        firstname="Google",
        lastname="User",
        email="google@example.com",
        username="googleuser",
        google_id="123456789",
        accountcreatedtime=now
    )
    
    # Verify user was created
    user = get_user_by_email("google@example.com")
    assert user is not None
    assert user["first_name"] == "Google"
    assert user["last_name"] == "User"
    assert user["google_id"] == "123456789"

def test_username_availability(test_db):
    """Test username availability check."""
    # Initially the username should be available
    assert is_username_available("newuser") == True
    
    # Create a user
    now = datetime.now()
    create_user(
        firstname="Test",
        lastname="User",
        email="test@example.com",
        username="newuser",
        password="testpass123",
        security_question="What is your favorite color?",
        security_answer="blue",
        accountcreatedtime=now
    )
    
    # Now the username should not be available
    assert is_username_available("newuser") == False

def test_email_availability(test_db):
    """Test email availability check."""
    # Initially the email should be available
    assert is_email_available("test@example.com") == True
    
    # Create a user
    now = datetime.now()
    create_user(
        firstname="Test",
        lastname="User",
        email="test@example.com",
        username="testuser",
        password="testpass123",
        security_question="What is your favorite color?",
        security_answer="blue",
        accountcreatedtime=now
    )
    
    # Now the email should not be available
    assert is_email_available("test@example.com") == False 