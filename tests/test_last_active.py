import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from bson import ObjectId

def test_complete_signup_sets_last_active(client):
    """
    Verify that /api/auth/complete-signup sets the last_active field.
    """
    mock_user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123"
    }
    
    with patch("routes.auth.db.users") as mock_users_col:
        mock_users_col.find_one.return_value = None  # No duplicate user
        mock_users_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch("routes.auth.create_access_token") as mock_token:
            mock_token.return_value = "fake_token"
            
            response = client.post(
                "/api/auth/complete-signup",
                json=mock_user_data
            )
            
            assert response.status_code == 201
            
            # Verify the call to insert_one included last_active
            args, kwargs = mock_users_col.insert_one.call_args
            inserted_doc = args[0]
            assert "last_active" in inserted_doc
            assert isinstance(inserted_doc["last_active"], datetime)
            assert inserted_doc["last_active"].tzinfo == timezone.utc

def test_set_password_signup_sets_last_active(client):
    """
    Verify that /api/auth/set-password (signup) sets the last_active field.
    """
    mock_data = {
        "email": "signupuser@example.com",
        "password": "password123",
        "purpose": "signup"
    }
    
    with patch("routes.auth.db.users") as mock_users_col:
        mock_users_col.find_one.return_value = None  # No duplicate user
        mock_users_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch("routes.auth.create_access_token") as mock_token:
            mock_token.return_value = "fake_token"
            
            response = client.post(
                "/api/auth/set-password",
                json=mock_data
            )
            
            assert response.status_code == 200
            
            # Verify the call to insert_one included last_active
            args, kwargs = mock_users_col.insert_one.call_args
            inserted_doc = args[0]
            assert "last_active" in inserted_doc
            assert isinstance(inserted_doc["last_active"], datetime)
            assert inserted_doc["last_active"].tzinfo == timezone.utc

def test_google_auth_new_user_sets_last_active(client):
    """
    Verify that /api/auth/google sets last_active for a new user.
    """
    mock_data = {"id_token": "valid_google_token"}
    mock_idinfo = {
        "email": "googleuser@example.com",
        "name": "Google User",
        "sub": "12345",
        "email_verified": True
    }
    
    with patch("routes.auth.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = mock_idinfo
        
        with patch("routes.auth.db.users") as mock_users_col:
            mock_users_col.find_one.return_value = None  # New user
            mock_users_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())
            
            with patch("routes.auth.create_access_token") as mock_token:
                mock_token.return_value = "fake_token"
                
                response = client.post(
                    "/api/auth/google",
                    json=mock_data
                )
                
                assert response.status_code == 200
                
                # Verify the call to insert_one included last_active
                args, kwargs = mock_users_col.insert_one.call_args
                inserted_doc = args[0]
                assert "last_active" in inserted_doc
                assert isinstance(inserted_doc["last_active"], datetime)
                assert inserted_doc["last_active"].tzinfo == timezone.utc
