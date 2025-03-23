def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_profile_page(client):
    """ Test proper redirection through 302 error code"""
    response = client.get('/profile')
    assert response.status_code == 302

def test_unauthorized_admin_access(client):
    """Test unauthorized access to admin route."""
    response = client.get('/admin')
    assert response.status_code == 200

def test_unauthorized_admin_users_access(client):
    response = client.get('/admin/users')
    assert response.status_code == 200

def test_register_page(client):
    """Test register page access."""
    response = client.get('/register')
    assert response.status_code == 200

def test_forgot_password_page(client):
    """Test forgot password page access."""
    response = client.get('/forgot_password')
    assert response.status_code == 200 