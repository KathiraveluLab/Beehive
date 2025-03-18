import pytest
from datetime import datetime
from pymongo import MongoClient
from Database.DatabaseConfig import DatabaseConfig
from Database.userdatahandler import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    check_username_availability,
    check_email_availability,
    create_google_user
)

def test_create_user(test_db):
    """Test user creation in database."""
    now = datetime.now()
    
    # First check username and email availability
    assert check_username_availability("testuser") == True
    assert check_email_availability("test@example.com") == True
    
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "security_question": "What is your favorite color?",
        "security_answer": "blue",
        "account_created_at": now
    }
    
    create_user(user_data)
    
    # Verify user was created
    user = get_user_by_email("test@example.com")
    assert user is not None
    assert user["first_name"] == "Test"
    assert user["last_name"] == "User"
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"

def test_create_google_user(test_db):
    """Test Google user creation in database."""
    now = datetime.now().isoformat()
    
    # First check username and email availability
    assert check_username_availability("googleuser") == True
    assert check_email_availability("google@example.com") == True
    
    user_data = {
        "first_name": "Google",
        "last_name": "User",
        "email": "google@example.com",
        "username": "googleuser",
        "google_id": "123456789",
        "account_created_at": now
    }
    
    create_google_user(user_data)
    
    # Verify user was created
    user = get_user_by_email("google@example.com")
    assert user is not None
    assert user["first_name"] == "Google"
    assert user["last_name"] == "User"
    assert user["google_id"] == "123456789"

def test_username_availability(test_db):
    """Test username availability check."""
    # Initially the username should be available
    assert check_username_availability("newuser") == True
    
    # Create a user
    now = datetime.now()
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "newuser",
        "password": "testpass123",
        "security_question": "What is your favorite color?",
        "security_answer": "blue",
        "account_created_at": now
    }
    
    create_user(user_data)
    
    # Now the username should not be available
    assert check_username_availability("newuser") == False

def test_email_availability(test_db):
    """Test email availability check."""
    # Initially the email should be available
    assert check_email_availability("test@example.com") == True
    
    # Create a user
    now = datetime.now()
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "security_question": "What is your favorite color?",
        "security_answer": "blue",
        "account_created_at": now
    }
    
    create_user(user_data)
    
    # Now the email should not be available
    assert check_email_availability("test@example.com") == False 