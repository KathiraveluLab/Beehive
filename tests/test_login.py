def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200