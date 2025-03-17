from datetime import datetime
import re

from flask import session

from Database.DatabaseConfig import DatabaseConfig

def get_admin_collection():
    return DatabaseConfig.get_beehive_admin_collection()

def create_admin(name: str, email: str, google_id: str, accountcreatedtime: datetime):
    
    admin_data = {
        "name" : name,
        "mail_id" : email,
        "google_id" : google_id,
        "account_created_at" : accountcreatedtime,
        "role" : "admin"
    }
    get_admin_collection().insert_one(admin_data)

def check_admin_available(google_id: str):
    query = {
        "google_id" : google_id
    }

    count = get_admin_collection().count_documents(query)
    return count == 0

def is_admin():
    # Check admin based on google_id (for Google sign-in)
    if 'google_id' in session:
        query = {
            "google_id": session['google_id']
        }
        admin = get_admin_collection().find_one(query)
        if admin and admin.get("role") == "admin":
            return True
    
    # Check admin based on email (for regular login)
    if 'email' in session:
        email = session['email']
        # Import the ALLOWED_EMAILS list if not available in this scope
        from OAuth.config import ALLOWED_EMAILS
        if email in ALLOWED_EMAILS:
            return True
        
    return False

def update_admin_profile_photo(google_id, filename):
    """Update the profile photo filename for an admin."""
    get_admin_collection().update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": filename}}
    )

def get_admin_by_google_id(google_id):
    """Get admin details by Google ID."""
    query = {
        "google_id": google_id
    }
    admin = get_admin_collection().find_one(query)
    return admin