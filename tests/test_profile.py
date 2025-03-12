from flask import session

def test_profile_authenticated(client):
    """Test access to profile page"""
    
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['email'] = 'test@example.com'
    
    response = client.get('/profile', follow_redirects=True) 

    assert response.status_code == 200