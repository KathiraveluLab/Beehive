from datetime import datetime
import re
from flask import session
from Database import DatabaseConfig
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# Initialize collections
beehive_user_collection = DatabaseConfig.get_beehive_user_collection()
beehive_image_collection = DatabaseConfig.get_beehive_image_collection()

if beehive_user_collection is None or beehive_image_collection is None:
    raise ValueError("❌ Database connection failed. User or Image collection is unavailable.")

# Create user in MongoDB
def create_user(firstname: str, lastname: str, email: str, username: str, password: str, account_created_time: datetime):
    """Registers a new user with hashed password"""
    try:
        user_data = {
            "first_name": firstname,
            "last_name": lastname,
            "mail_id": email,
            "username": username,
            "password": generate_password_hash(password),  # Secure password storage
            "account_created_at": account_created_time,
            "role": "user"
        }
        result = beehive_user_collection.insert_one(user_data)
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

# Check if username is available
def is_username_available(username: str) -> bool:
    try:
        return beehive_user_collection.find_one({"username": username}) is None
    except Exception as e:
        print(f"❌ Error checking username: {e}")
        return False

# Check if email is available
def is_email_available(email: str) -> bool:
    try:
        return beehive_user_collection.find_one({"mail_id": email}) is None
    except Exception as e:
        print(f"❌ Error checking email: {e}")
        return False

# Validate email format
def is_valid_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return bool(re.fullmatch(regex, email))

# Get user password (hashed) by username
def get_password_by_username(username: str):
    try:
        user = beehive_user_collection.find_one({"username": username})
        return user["password"] if user else None
    except Exception as e:
        print(f"❌ Error retrieving password: {e}")
        return None

# Get user details by username
def get_user_by_username(username: str):
    try:
        return beehive_user_collection.find_one({"username": username})
    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
        return None

# Save image to MongoDB
def save_image(username: str, filename: str, title: str, description: str):
    """Saves an image with metadata"""
    try:
        image_data = {
            "username": username,
            "filename": filename,
            "title": title,
            "description": description
        }
        beehive_image_collection.insert_one(image_data)
    except Exception as e:
        print(f"❌ Error saving image: {e}")

# Get all users
def get_all_users():
    try:
        return list(beehive_user_collection.find({}, {"password": 0}))  # Exclude passwords
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
        return []

# Get current user from session
def get_current_user_from_session():
    """Retrieves the current logged-in user from session"""
    try:
        user_data = session.get("user")
        if not user_data or "user_id" not in user_data:
            return None
        return beehive_user_collection.find_one({"_id": ObjectId(user_data["user_id"])})
    except Exception as e:
        print(f"❌ Error retrieving current user: {e}")
        return None

# Get all images uploaded by a user
def get_images_by_user(username: str):
    try:
        images = beehive_image_collection.find({"username": username})
        return [
            {"id": str(image["_id"]), "filename": image["filename"], "title": image["title"], "description": image["description"]}
            for image in images
        ]
    except Exception as e:
        print(f"❌ Error retrieving images: {e}")
        return []

# Update image metadata
def update_image(image_id: str, title: str, description: str):
    try:
        beehive_image_collection.update_one(
            {"_id": ObjectId(image_id)},
            {"$set": {"title": title, "description": description}}
        )
    except Exception as e:
        print(f"❌ Error updating image: {e}")

# Delete image from MongoDB
def delete_image(image_id: str):
    try:
        beehive_image_collection.delete_one({"_id": ObjectId(image_id)})
    except Exception as e:
        print(f"❌ Error deleting image: {e}")

# Get image by ID
def get_image_by_id(image_id: str):
    try:
        return beehive_image_collection.find_one({"_id": ObjectId(image_id)})
    except Exception as e:
        print(f"❌ Error retrieving image: {e}")
        return None
