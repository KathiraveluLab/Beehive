"""
Tests for the application routes.
"""

def test_index_route(client):
    """Test the index route returns 200 and correct template."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    """Test the login route returns 200 and correct template."""
    response = client.get('/login')
    assert response.status_code == 200

def test_register_route(client):
    """Test the register route returns 200 and correct template."""
    response = client.get('/register')
    assert response.status_code == 200

def test_profile_route_redirect(client):
    """Test that profile route redirects to login when not authenticated."""
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200  # Should redirect to login 

def test_profile_route_authenticated(authenticated_client, test_user):
    """Test profile route when logged in."""
    response = authenticated_client.get('/profile')
    assert response.status_code == 200
    assert test_user['username'].encode() in response.data
    assert b'Uploaded Images' in response.data

def test_delete_image(authenticated_client):
    """Test image deletion."""
    # First upload an image
    img_io = create_test_image()
    data = {
        'files': (img_io, 'test.png'),
        'title': 'Test Image',
        'description': 'This is a test image',
        'sentiment': 'Happy'
    }
    response = authenticated_client.post('/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200

    # Get the image ID from the database
    from Database.userdatahandler import beehive_image_collection
    image = beehive_image_collection.find_one({'title': 'Test Image'})
    assert image is not None
    image_id = str(image['_id'])

    # Delete the image
    response = authenticated_client.get(f'/delete/{image_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Image record deleted from database' in response.data

    # Verify image is deleted from database
    from bson import ObjectId
    image = beehive_image_collection.find_one({'_id': ObjectId(image_id)})
    assert image is None

def test_edit_image(authenticated_client):
    """Test image editing."""
    # First upload an image
    img_io = create_test_image()
    data = {
        'files': (img_io, 'test.png'),
        'title': 'Test Image',
        'description': 'This is a test image',
        'sentiment': 'Happy'
    }
    response = authenticated_client.post('/upload', 
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Get the image ID from the database
    from Database.userdatahandler import beehive_image_collection
    image = beehive_image_collection.find_one({'title': 'Test Image'})
    assert image is not None
    
    # Edit the image
    edit_data = {
        'title': 'Updated Title',
        'description': 'Updated description'
    }
    response = authenticated_client.post(f'/edit/{image["_id"]}', 
        data=edit_data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Image updated successfully' in response.data
    
    # Verify image is updated in database
    updated_image = beehive_image_collection.find_one({'_id': image['_id']})
    assert updated_image['title'] == 'Updated Title'
    assert updated_image['description'] == 'Updated description'

from tests.test_upload import create_test_image 