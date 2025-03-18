from datetime import datetime
import re

from flask import session

from Database.DatabaseConfig import DatabaseConfig

def get_admin_collection():
    return DatabaseConfig.get_beehive_admin_collection()

def create_admin(admin_data):
    """Create a new admin user."""
    return DatabaseConfig.get_beehive_admin_collection().insert_one(admin_data)

def check_admin_available():
    """Check if any admin exists in the database."""
    return DatabaseConfig.get_beehive_admin_collection().count_documents({}) > 0

def is_admin(session):
    """Check if the current user is an admin."""
    if "google_id" not in session:
        return False
    return DatabaseConfig.get_beehive_admin_collection().find_one({"google_id": session["google_id"]}) is not None

def update_admin_profile_photo(google_id, profile_photo):
    """Update admin's profile photo."""
    return DatabaseConfig.get_beehive_admin_collection().update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": profile_photo}}
    )

def get_admin_by_google_id(google_id):
    """Get admin details by Google ID."""
    return DatabaseConfig.get_beehive_admin_collection().find_one({"google_id": google_id})