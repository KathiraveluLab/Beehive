from datetime import datetime
from pymongo.errors import PyMongoError
from flask import session

from database import databaseConfig
from utils.logger import Logger

logger = Logger.get_logger("admin_handler")

def create_admin(name: str, email: str, google_id: str, account_created_time: datetime):
    beehive_admin_collection = databaseConfig.get_beehive_admin_collection()

    if beehive_admin_collection.find_one({"google_id": google_id}):
        raise ValueError("Admin with this google_id already exists")
    
    admin_data = {
        "name" : name,
        "mail_id" : email,
        "google_id" : google_id,
        "account_created_at" : account_created_time,
        "role" : "admin"
    }
    try:
        result = beehive_admin_collection.insert_one(admin_data)
        return result.inserted_id
    except PyMongoError:
         logger.error(
             "Failed to create admin for google_id=%s, email=%s",
             google_id,
             email,
             exc_info=True
         )
         raise

def is_admin_available(google_id: str) -> bool:
    
    beehive_admin_collection = databaseConfig.get_beehive_admin_collection()

    count = beehive_admin_collection.count_documents({"google_id" : google_id}, limit=1)
    return count == 0

def is_admin() -> bool:
    beehive_admin_collection = databaseConfig.get_beehive_admin_collection()
    # Check admin based on google_id (for Google sign-in)
    google_id=session.get("google_id")
    if google_id:
        admin = beehive_admin_collection.find_one({"google_id" : google_id})
        if admin and admin.get("role") == "admin":
            return True
    
    # Check admin based on email (for regular login)
    email=session.get("email")
    if email:
        # Check against DB first using 'mail_id'
        admin = beehive_admin_collection.find_one({"mail_id": email})
        if admin and admin.get("role") == "admin":
            return True

        # Fallback to config file
        try:
            from oauth.config import ALLOWED_EMAILS
            
            if email in ALLOWED_EMAILS:
                logger.warning(
                    "Admin access granted via ALLOWED_EMAILS fallback for %s",
                    email,
                )
                return True
        except ImportError:
            logger.warning("Could not import ALLOWED_EMAILS from oauth.config")
            
    return False

def update_admin_profile_photo(google_id: str, filename: str) -> bool:
    """Update the profile photo filename for an admin."""
    beehive_admin_collection = databaseConfig.get_beehive_admin_collection()
    try:
        result = beehive_admin_collection.update_one(
            {"google_id": google_id},
            {"$set": {"profile_photo": filename}}
        )
        return result.modified_count > 0
    except PyMongoError:
        logger.error(f"Failed to update photo for google_id={google_id}", exc_info=True)
        return False

def get_admin_by_google_id(google_id: str) -> dict | None:
    """Get admin details by Google ID."""
    beehive_admin_collection = databaseConfig.get_beehive_admin_collection()
    return beehive_admin_collection.find_one({"google_id": google_id})
