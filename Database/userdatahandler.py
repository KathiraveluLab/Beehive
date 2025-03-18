from datetime import datetime, timedelta
import re
import bcrypt
from flask import session
from Database.DatabaseConfig import DatabaseConfig

def get_user_collection():
    return DatabaseConfig.get_beehive_user_collection()

def get_image_collection():
    return DatabaseConfig.get_beehive_image_collection()

# Create user in MongoDB
def create_user(user_data):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.insert_one(user_data)

# Check if username is available in MongoDB for registration purpose
def check_username_availability(username):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.count_documents({"username": username}) == 0

def check_email_availability(email):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.count_documents({"email": email}) == 0

def is_valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return bool(re.fullmatch(regex, email))

# Get password by username from MongoDB
def get_password_by_username(username):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    user = user_collection.find_one({"username": username})
    return user.get("password") if user else None
    
# Get user by username from MongoDB
def get_user_by_username(username):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"username": username})

def get_user_by_email(email):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"email": email})

def create_google_user(user_data):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.insert_one(user_data)

def update_user_profile_photo(user_id, profile_photo):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.update_one(
        {"_id": user_id},
        {"$set": {"profile_photo": profile_photo}}
    )

def update_username(user_id, new_username):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.update_one(
        {"_id": user_id},
        {"$set": {"username": new_username}}
    )
    
    
def update_email(user_id, new_email):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.update_one(
        {"_id": user_id},    
        {"$set": {"mail_id": new_email}}
    )

def update_password(user_id, new_password):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    return user_collection.update_one(
        {"_id": user_id},
        {"$set": {"password": hashed_password}}
    )
    
# Save image to MongoDB  
def save_image(image_data):
    image_collection = DatabaseConfig.get_beehive_image_collection()
    return image_collection.insert_one(image_data)

# Count all images from MongoDB
def total_images():
    image_collection = DatabaseConfig.get_beehive_image_collection()
    return image_collection.count_documents({})

# Count all images from MongoDB uploaded today
def todays_images():
    image_collection = DatabaseConfig.get_beehive_image_collection()
    last_24_hours = datetime.now() - timedelta(hours=24)
    return image_collection.count_documents({
        "created_at": {"$gte": last_24_hours}
    })

def get_all_users():
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find()

def get_current_user_from_session():
    user_data = session.get('user')
    if not user_data or not user_data.get('user_id'):
        return None
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({'_id': user_data['user_id']})

# Get all images from MongoDB
def get_images_by_user(username):
    image_collection = DatabaseConfig.get_beehive_image_collection()
    images = image_collection.find({'username': username})
    return [{
        'id': str(image['_id']),
        'filename': image['filename'],
        'title': image['title'],
        'description': image['description'],
        'audio_filename': image.get('audio_filename', ""),
        'sentiment': image.get('sentiment', "")
    } for image in images]

# Update image in MongoDB
def update_image(image_id, title, description):
    image_collection = DatabaseConfig.get_beehive_image_collection()
    return image_collection.update_one(
        {'_id': image_id},
        {'$set': {'title': title, 'description': description}}
    )

# Delete image from MongoDB
def delete_image(image_id):
    image_collection = DatabaseConfig.get_beehive_image_collection()
    return image_collection.delete_one({'_id': image_id})

# Get image by id from MongoDB
def get_image_by_id(image_id):
    image_collection = DatabaseConfig.get_beehive_image_collection()
    return image_collection.find_one({'_id': image_id})

def get_user_by_google_id(google_id):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"google_id": google_id})

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))
