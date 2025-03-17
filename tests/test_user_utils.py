from usersutils.valid_username import is_valid_username

def test_valid_username():
    """Test valid username cases."""
    assert is_valid_username("user123") == True
    assert is_valid_username("validuser") == True
    assert is_valid_username("test_user") == True
    assert is_valid_username("a" * 25) == True  # Max length

def test_invalid_username():
    """Test invalid username cases."""
    # Empty username
    assert is_valid_username("") == False
    # Too short
    assert is_valid_username("abc") == False
    # Too long
    assert is_valid_username("a" * 26) == False 