def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200