"""
This module handles Google OAuth functionality.
"""

def get_user_info(token=None):
    """
    Mock function for testing - returns user info based on token.
    In production, this would make a real API call to Google.
    """
    # For testing purposes, return mock data
    return {
        "email": "user@example.com",
        "given_name": "Test",
        "family_name": "User"
    } 