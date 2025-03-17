def test_index_route(client):
    """Test the index route returns 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_app_is_testing(app):
    """Test that the app is in testing mode."""
    assert app.config['TESTING'] == True 