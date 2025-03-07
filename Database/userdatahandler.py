from datetime import datetime, timedelta
import re

import bcrypt
 dev
from flask import session
from Database import DatabaseConfig
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# Initialize collections
beehive_user_collection = DatabaseConfig.get_beehive_user_collection()
beehive_image_collection = DatabaseConfig.get_beehive_image_collection()

import bcrypt  # Keeping bcrypt as it's required for password hashing

# Ensure database collections are available before proceeding
if beehive_user_collection is None or beehive_image_collection is None:
    raise ValueError("❌ Database connection failed. User or Image collection is unavailable.")

# Create user in MongoDB
def create_user(firstname: str, lastname: str, email: str, username: str, password: str, security_question: str, security_answer: str, accountcreatedtime: datetime):
    """Creates a new user in MongoDB with hashed password and security answer."""
    
    # Hash the password before storing
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_answer = bcrypt.hashpw(security_answer.encode('utf-8'), salt)
    
    user_data = {
        "first_name": firstname,
        "last_name": lastname,
        "mail_id": email,
        "username": username,
        "password": hashed_password,
        "security_question": security_question,
        "security_answer": hashed_answer,  
        "account_created_at": accountcreatedtime,
        "role": "user"
    }
    
    user_inserted_id = beehive_user_collection.insert_one(user_data).inserted_id
    return user_inserted_id  # Returning the inserted user's ID for reference

# Check if username is available in MongoDB for registration purposes
def is_username_available(username: str) -> bool:
    """Checks if a username is already taken in the database."""
    query = {"username": username}
    existing_user = beehive_user_collection.find_one(query)
    return existing_user is None  # Returns True if username is available

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
# Retrieve the hashed password for a given username
def get_password_by_username(username: str):
    """Fetches the hashed password of a user by username."""
    try:
        user = beehive_user_collection.find_one({"username": username})
        return user.get("password") if user else None
    except Exception as e:
        print(f"❌ Error retrieving password: {e}")
        return None

# Get user by username from MongoDB
def get_user_by_username(username: str):
    """Fetch user details by username."""
    return beehive_user_collection.find_one({"username": username})

# Get user by email from MongoDB
def get_user_by_email(email: str):
    """Fetch user details by email."""
    return beehive_user_collection.find_one({"mail_id": email})

# Create a user that will authenticate via Google
def create_google_user(firstname: str, lastname: str, email: str, username: str, google_id: str, accountcreatedtime: str):
    """Create a new user for Google-based authentication."""
    user_data = {
        "first_name": firstname,
        "last_name": lastname,
        "mail_id": email,
        "username": username,
        "google_id": google_id,
        "account_created_at": accountcreatedtime,
        "role": "user"
    }
    return beehive_user_collection.insert_one(user_data).inserted_id

# Update user profile photo
def update_profile_photo(username, filename):
    """Update the profile picture filename for a user."""
    beehive_user_collection.update_one(
        {"username": username},
        {"$set": {"profile_photo": filename}}
    )

# Update username
def update_username(user_id, new_username):    
    """Modify a user's username."""
    beehive_user_collection.update_one(
        {"_id": user_id},
        {"$set": {"username": new_username}}
    )

# Update email
def update_email(user_id, new_email):
    """Modify a user's email address."""
    beehive_user_collection.update_one(
        {"_id": user_id},    
        {"$set": {"mail_id": new_email}}
    )

# Update password with hashing
def update_password(user_id, new_password):
    """Modify a user's password and hash it before storing."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    beehive_user_collection.update_one(
        {"_id": user_id},
        {"$set": {"password": hashed_password}}
    )

# Save an image to MongoDB
def save_image(username, filename, title, description, time_created, audio_filename=None, sentiment=None):
    """Store image metadata in the database."""
    image = {
        'username': username,
        'filename': filename,
        'title': title,
        'description': description,
        'created_at': time_created,
        'audio_filename': audio_filename,
        'sentiment': sentiment
    }
    beehive_image_collection.insert_one(image)

# Count all images in MongoDB
def total_images():
    """Count the total number of uploaded images."""
    return beehive_image_collection.count_documents({})

# Count all images uploaded today
def todays_images():
    """Count images uploaded in the last 24 hours."""
    last_24_hours = datetime.now() - timedelta(hours=24)
    return beehive_image_collection.count_documents({
        "created_at": {"$gte": last_24_hours}
    })

# Retrieve all users
def get_all_users():
    """Fetch all registered users from the database."""
    return beehive_user_collection.find()

# Get user details by username
def get_user_by_username(username: str):
    try:
        return beehive_user_collection.find_one({"username": username})
    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
        return None

from bson import ObjectId

# Save image to MongoDB
def save_image(username: str, filename: str, title: str, description: str, audio_filename=None, sentiment=None):
    """Saves an image with metadata."""
    try:
        image_data = {
            "username": username,
            "filename": filename,
            "title": title,
            "description": description,
            "audio_filename": audio_filename,
            "sentiment": sentiment
        }
        beehive_image_collection.insert_one(image_data)
    except Exception as e:
        print(f"❌ Error saving image: {e}")

# Get all images uploaded by a user
def get_images_by_user(username: str):
    """Retrieve all images uploaded by a specific user."""
    try:
        images = beehive_image_collection.find({'username': username})
        return [{
            'id': str(image['_id']),
            'filename': image['filename'],
            'title': image['title'],
            'description': image['description'],
            'audio_filename': image.get('audio_filename', ""),
            'sentiment': image.get('sentiment', "")
        } for image in images]
    except Exception as e:
        print(f"❌ Error retrieving images for user {username}: {e}")
        return []

# Get all users (excluding passwords)
def get_all_users():
    """Retrieve all users from the database, excluding passwords."""
    try:
        return list(beehive_user_collection.find({}, {"password": 0}))  # Exclude passwords for security
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
        return []

# Get current logged-in user from session
def get_current_user_from_session():
    """Retrieves the currently logged-in user from the session."""
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
