from datetime import datetime
import re

from flask import session

from Database.DatabaseConfig import DatabaseConfig

def create_admin(admin_data):
    """Create a new admin user in the database.
    
    Args:
        admin_data (dict): Dictionary containing admin information
        
    Returns:
        InsertOneResult: Result of the insert operation
    """
    return DatabaseConfig.get_beehive_admin_collection().insert_one(admin_data)

def check_admin_available():
    """Check if any admin exists in the database.
    
    Returns:
        bool: True if at least one admin exists, False otherwise
    """
    return DatabaseConfig.get_beehive_admin_collection().count_documents({}) > 0

def is_admin(session):
    """Check if the current user is an admin.
    
    Args:
        session (dict): Flask session object
        
    Returns:
        bool: True if user is an admin, False otherwise
    """
    if "google_id" not in session:
        return False
    return DatabaseConfig.get_beehive_admin_collection().find_one({"google_id": session["google_id"]}) is not None

def update_admin_profile_photo(google_id, profile_photo):
    """Update admin's profile photo.
    
    Args:
        google_id (str): Google ID of the admin
        profile_photo (str): URL of the new profile photo
        
    Returns:
        UpdateResult: Result of the update operation
    """
    return DatabaseConfig.get_beehive_admin_collection().update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": profile_photo}}
    )

def get_admin_by_google_id(google_id):
    """Get admin details by Google ID.
    
    Args:
        google_id (str): Google ID of the admin
        
    Returns:
        dict: Admin document if found, None otherwise
    """
    return DatabaseConfig.get_beehive_admin_collection().find_one({"google_id": google_id})