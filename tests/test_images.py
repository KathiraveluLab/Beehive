import pytest
from datetime import datetime
from bson import ObjectId
from Database.userdatahandler import (
    save_image,
    get_images_by_user,
    update_image,
    delete_image,
    get_image_by_id,
    total_images,
    todays_images,
    create_user
)

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
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
    return "testuser"

@pytest.fixture
def sample_image_data(test_user):
    """Fixture to provide sample image data."""
    return {
        'username': test_user,
        'filename': 'test.jpg',
        'title': 'Test Image',
        'description': 'A test image description',
        'created_at': datetime.now(),
        'audio_filename': 'test_audio.mp3',
        'sentiment': 'positive'
    }

def test_save_and_get_image(test_db, test_user, sample_image_data):
    """Test saving and retrieving an image."""
    # Ensure no images exist initially
    initial_images = get_images_by_user(test_user)
    assert len(initial_images) == 0
    
    # Save the image
    save_image(sample_image_data)
    
    # Get images for the user
    images = get_images_by_user(sample_image_data['username'])
    assert len(images) == 1
    image = images[0]
    assert image['filename'] == sample_image_data['filename']
    assert image['title'] == sample_image_data['title']
    assert image['description'] == sample_image_data['description']

def test_update_image(test_db, test_user, sample_image_data):
    """Test updating an image."""
    # First save the image
    save_image(sample_image_data)
    
    # Get the image to get its ID
    images = get_images_by_user(sample_image_data['username'])
    assert len(images) == 1
    image_id = ObjectId(images[0]['id'])
    
    # Update the image
    new_title = "Updated Title"
    new_description = "Updated description"
    update_image(image_id, new_title, new_description)
    
    # Verify the update
    updated_image = get_image_by_id(image_id)
    assert updated_image['title'] == new_title
    assert updated_image['description'] == new_description

def test_delete_image(test_db, test_user, sample_image_data):
    """Test deleting an image."""
    # Ensure no images exist initially
    initial_images = get_images_by_user(test_user)
    assert len(initial_images) == 0
    
    # First save the image
    save_image(sample_image_data)
    
    # Get the image to get its ID
    images = get_images_by_user(sample_image_data['username'])
    assert len(images) == 1
    image_id = ObjectId(images[0]['id'])
    
    # Delete the image
    delete_image(image_id)
    
    # Verify the image was deleted
    images_after = get_images_by_user(sample_image_data['username'])
    assert len(images_after) == 0

def test_image_counts(test_db, test_user, sample_image_data):
    """Test image counting functions."""
    # Ensure no images exist initially
    assert total_images() == 0
    assert todays_images() == 0
    
    # Add an image
    save_image(sample_image_data)
    
    # Check counts
    assert total_images() == 1
    assert todays_images() == 1 