"""
Tests for image upload functionality.
"""

import io
import os
from PIL import Image

def create_test_image():
    """Create a test image file."""
    # Create a new image with a red background
    image = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def test_upload_image(authenticated_client):
    """Test image upload functionality."""
    # Create test image
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
    assert b'Image uploaded successfully!' in response.data

def test_upload_invalid_file(authenticated_client):
    """Test upload with invalid file type."""
    # Create an invalid file (text file)
    text_io = io.BytesIO(b'This is not an image')
    
    data = {
        'files': (text_io, 'test.txt'),
        'title': 'Test File',
        'description': 'This is a test file',
        'sentiment': 'Happy'
    }
    
    response = authenticated_client.post('/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Invalid file type' in response.data 