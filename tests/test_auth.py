from database.userdatahandler import get_user_by_username 


def test_register_success(client):
    """Test successful registration."""
    response = client.post("/register", data={
        "firstname": "Test",
        "lastname": "User",
        "email": "test123@gmail.com",
        "username": "testuser123",
        "password": "password123",
        "confirm_password": "password123",
        "security_question": "What is your favorite book?",
        "security_answer": "1984"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration successful!" in response.data

    # Check if user was added to the database
    user = get_user_by_username("testuser123")
    assert user is not None
    assert user["mail_id"] == "test123@gmail.com"

def test_register_password_mismatch(client):
    """Test registration failure due to mismatched passwords."""
    response = client.post("/register", data={
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "username": "testuser123",
        "password": "password123",
        "confirm_password": "wrongpassword",
        "security_question": "What is your favorite book?",
        "security_answer": "1984"
    })

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data



