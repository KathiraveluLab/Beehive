from datetime import datetime
import re

from flask import session

from Database import DatabaseConfig

beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()

def create_admin(name: str, email: str, google_id: str, accountcreatedtime: datetime):
    
    admin_data = {
        "name" : name,
        "mail_id" : email,
        "google_id" : google_id,
        "account_created_at" : accountcreatedtime,
        "role" : "admin"
    }
    admin_inserted_id = beehive_admin_collection.insert_one(admin_data).inserted_id

def check_admin_available(google_id: str):
    query = {
        "google_id" : google_id
    }

    count = beehive_admin_collection.count_documents(query)
    return count == 0

def is_admin():
    if 'google_id' in session:
        query = {
            "google_id": session['google_id']
        }
        admin = beehive_admin_collection.find_one(query)
        if admin and admin.get("role") == "admin":
            return True
    return False

def update_admin_profile_photo(google_id, filename):
    """Update the profile photo filename for an admin."""
    beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()
    beehive_admin_collection.update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": filename}}
    )

def get_admin_by_google_id(google_id):
    """Get admin details by Google ID."""
    beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()
    query = {
        "google_id": google_id
    }
    admin = beehive_admin_collection.find_one(query)
    return admin