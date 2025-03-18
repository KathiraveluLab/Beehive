from datetime import datetime, timedelta
import re
import bcrypt
from flask import session
from Database.DatabaseConfig import DatabaseConfig

def create_user(user_data):
    """Create a new user in the database.
    
    Args:
        user_data (dict): Dictionary containing user information
        
    Returns:
        InsertOneResult: Result of the insert operation
    """
    return DatabaseConfig.get_beehive_user_collection().insert_one(user_data)

def check_username_availability(username):
    """Check if a username is available.
    
    Args:
        username (str): Username to check
        
    Returns:
        bool: True if username is available, False otherwise
    """
    return DatabaseConfig.get_beehive_user_collection().count_documents({"username": username}) == 0

def check_email_availability(email):
    """Check if an email is available.
    
    Args:
        email (str): Email to check
        
    Returns:
        bool: True if email is available, False otherwise
    """
    return DatabaseConfig.get_beehive_user_collection().count_documents({"email": email}) == 0

def is_valid_email(email):
    """Validate email format.
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return bool(re.fullmatch(regex, email))

def get_password_by_username(username):
    """Get hashed password by username.
    
    Args:
        username (str): Username to look up
        
    Returns:
        str: Hashed password if found, None otherwise
    """
    user = DatabaseConfig.get_beehive_user_collection().find_one({"username": username})
    return user.get("password") if user else None

def get_user_by_username(username):
    """Get user details by username.
    
    Args:
        username (str): Username to look up
        
    Returns:
        dict: User document if found, None otherwise
    """
    return DatabaseConfig.get_beehive_user_collection().find_one({"username": username})

def get_user_by_email(email):
    """Get user details by email.
    
    Args:
        email (str): Email to look up
        
    Returns:
        dict: User document if found, None otherwise
    """
    return DatabaseConfig.get_beehive_user_collection().find_one({"email": email})

def create_google_user(user_data):
    """Create a new user with Google authentication.
    
    Args:
        user_data (dict): Dictionary containing Google user information
        
    Returns:
        InsertOneResult: Result of the insert operation
    """
    return DatabaseConfig.get_beehive_user_collection().insert_one(user_data)

def update_user_profile_photo(google_id, profile_photo):
    """Update user's profile photo.
    
    Args:
        google_id (str): Google ID of the user
        profile_photo (str): URL of the new profile photo
        
    Returns:
        UpdateResult: Result of the update operation
    """
    return DatabaseConfig.get_beehive_user_collection().update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": profile_photo}}
    )

def update_username(user_id, new_username):
    """Update user's username.
    
    Args:
        user_id (ObjectId): User's database ID
        new_username (str): New username
        
    Returns:
        UpdateResult: Result of the update operation
    """
    return DatabaseConfig.get_beehive_user_collection().update_one(
        {"_id": user_id},
        {"$set": {"username": new_username}}
    )

def update_email(user_id, new_email):
    """Update user's email.
    
    Args:
        user_id (ObjectId): User's database ID
        new_email (str): New email address
        
    Returns:
        UpdateResult: Result of the update operation
    """
    return DatabaseConfig.get_beehive_user_collection().update_one(
        {"_id": user_id},    
        {"$set": {"mail_id": new_email}}
    )

def update_password(user_id, new_password):
    """Update user's password with bcrypt hashing.
    
    Args:
        user_id (ObjectId): User's database ID
        new_password (str): New password to hash and store
        
    Returns:
        UpdateResult: Result of the update operation
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    return DatabaseConfig.get_beehive_user_collection().update_one(
        {"_id": user_id},
        {"$set": {"password": hashed_password}}
    )

def save_image(image_data):
    """Save image metadata to database.
    
    Args:
        image_data (dict): Dictionary containing image information
        
    Returns:
        InsertOneResult: Result of the insert operation
    """
    return DatabaseConfig.get_beehive_image_collection().insert_one(image_data)

def total_images():
    """Get total count of images in database.
    
    Returns:
        int: Total number of images
    """
    return DatabaseConfig.get_beehive_image_collection().count_documents({})

def todays_images():
    """Get count of images uploaded in last 24 hours.
    
    Returns:
        int: Number of images uploaded today
    """
    last_24_hours = datetime.now() - timedelta(hours=24)
    return DatabaseConfig.get_beehive_image_collection().count_documents({
        "created_at": {"$gte": last_24_hours}
    })

def get_all_users():
    """Get all users from database.
    
    Returns:
        Cursor: MongoDB cursor containing all user documents
    """
    return DatabaseConfig.get_beehive_user_collection().find()

def get_current_user_from_session():
    """Get current user from session.
    
    Returns:
        dict: Current user document if found, None otherwise
    """
    user_data = session.get('user')
    if not user_data or not user_data.get('user_id'):
        return None
    return DatabaseConfig.get_beehive_user_collection().find_one({'_id': user_data['user_id']})

def get_images_by_user(username):
    """Get all images uploaded by a user.
    
    Args:
        username (str): Username to look up
        
    Returns:
        list: List of image documents with formatted fields
    """
    images = DatabaseConfig.get_beehive_image_collection().find({'username': username})
    return [{
        'id': str(image['_id']),
        'filename': image['filename'],
        'title': image['title'],
        'description': image['description'],
        'audio_filename': image.get('audio_filename', ""),
        'sentiment': image.get('sentiment', "")
    } for image in images]

def update_image(image_id, title, description):
    """Update image metadata.
    
    Args:
        image_id (ObjectId): Image's database ID
        title (str): New title
        description (str): New description
        
    Returns:
        UpdateResult: Result of the update operation
    """
    return DatabaseConfig.get_beehive_image_collection().update_one(
        {'_id': image_id},
        {'$set': {'title': title, 'description': description}}
    )

def delete_image(image_id):
    """Delete an image from database.
    
    Args:
        image_id (ObjectId): Image's database ID
        
    Returns:
        DeleteResult: Result of the delete operation
    """
    return DatabaseConfig.get_beehive_image_collection().delete_one({'_id': image_id})

def get_image_by_id(image_id):
    """Get image by ID.
    
    Args:
        image_id (ObjectId): Image's database ID
        
    Returns:
        dict: Image document if found, None otherwise
    """
    return DatabaseConfig.get_beehive_image_collection().find_one({'_id': image_id})

def get_user_by_google_id(google_id):
    """Get user details by Google ID.
    
    Args:
        google_id (str): Google ID to look up
        
    Returns:
        dict: User document if found, None otherwise
    """
    return DatabaseConfig.get_beehive_user_collection().find_one({"google_id": google_id})

def is_valid_username(username):
    """Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if username is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9_]{3,20}$"
    return bool(re.match(pattern, username))
