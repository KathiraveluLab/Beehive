def test_logout(client):
    with client.session_transaction() as session:
        session['username'] = 'testuser'
        session['google_id'] = '12345'
        session['name'] = 'Test User'
        session['email'] = 'test@example.com'
    
    response = client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    
    with client.session_transaction() as session:
        assert 'username' not in session
        assert 'google_id' not in session
        assert 'name' not in session
        assert 'email' not in session
    
    # Test flash message and redirect
    assert b'You have been logged out.' in response.data
    assert b'login' in response.data