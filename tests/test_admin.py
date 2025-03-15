"""
Tests for admin functionality.
"""
import os
import pytest
from unittest.mock import patch
from bson import ObjectId
from Database.admindatahandler import beehive_admin_collection
from Database.userdatahandler import beehive_image_collection
from tests.test_upload import create_test_image

@pytest.fixture
def admin_data():
    """Admin test data."""
    return {
        'name': 'Test Admin',
        'mail_id': 'admin@test.com',
        'google_id': '123456789',
        'role': 'admin'
    }

@pytest.fixture
def admin_client(client, admin_data):
    """Create an authenticated admin client."""
    with client.session_transaction() as session:
        session['google_id'] = admin_data['google_id']
        session['name'] = admin_data['name']
        session['email'] = admin_data['mail_id']
    
    # Insert admin into database
    beehive_admin_collection.insert_one(admin_data)
    
    yield client
    
    # Cleanup
    beehive_admin_collection.delete_one({'google_id': admin_data['google_id']})

def test_admin_login_page(client):
    """Test admin login page."""
    response = client.get('/signingoogle')
    assert response.status_code == 200
    assert b'Sign in with Google' in response.data

def test_admin_dashboard_access(admin_client):
    """Test admin dashboard access."""
    response = admin_client.get('/admin')
    assert response.status_code == 200
    assert b'Admin' in response.data
    assert b'View Users' in response.data

def test_admin_dashboard_unauthorized(client):
    """Test unauthorized access to admin dashboard."""
    response = client.get('/admin')
    assert response.status_code == 200  # Returns 403 page
    assert b"You don't have permission to access this page" in response.data

def test_admin_view_users(admin_client, test_user):
    """Test admin viewing all users."""
    response = admin_client.get('/admin/users')
    assert response.status_code == 200
    assert bytes(test_user['username'], 'utf-8') in response.data

def test_admin_view_user_images(admin_client, test_user):
    """Test admin viewing a specific user's images."""
    # First upload an image for the test user
    img_io = create_test_image()
    data = {
        'files': (img_io, 'test.png'),
        'title': 'Test Image',
        'description': 'This is a test image',
        'sentiment': 'Happy'
    }
    
    # Create a client for the test user
    with admin_client.session_transaction() as session:
        session['username'] = test_user['username']
    
    response = admin_client.post('/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Now test admin viewing the user's images
    with admin_client.session_transaction() as session:
        session.pop('username', None)  # Remove user session
        session['google_id'] = '123456789'  # Restore admin session
    
    response = admin_client.get(f'/admin/users/{test_user["username"]}')
    assert response.status_code == 200
    assert b'Test Image' in response.data

def test_admin_reset_password(admin_client, test_user):
    """Test admin resetting user password."""
    data = {
        'username': test_user['username'],
        'new_password': 'newpassword123'
    }
    response = admin_client.post('/admin/reset_password',
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'success' in response.data

def test_admin_upload_profile_photo(admin_client, admin_data):
    """Test admin profile photo upload."""
    img_io = create_test_image()
    data = {
        'profile_photo': (img_io, 'admin_profile.png')
    }
    response = admin_client.post('/upload_admin_profile_photo',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Verify the photo was saved
    admin = beehive_admin_collection.find_one({'google_id': admin_data['google_id']})
    assert admin.get('profile_photo') is not None
    
    # Cleanup
    photo_path = os.path.join('static/uploads/profile', admin['profile_photo'])
    if os.path.exists(photo_path):
        os.remove(photo_path) 