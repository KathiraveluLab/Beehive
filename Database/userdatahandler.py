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

def isValidEmail(email):
  regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

  if re.fullmatch(regex, email):
    return True

  return False
# Get password by username from MongoDB
def get_password_by_username(username: str):
    query = {
        "username" : username
    }
    user = get_user_collection().find_one(query)
    if user:
        return user.get("password")
    else:
        return None
    
# Get user by username from MongoDB
def get_user_by_username(username):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"username": username})

def get_user_by_email(email):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"email": email})

def create_google_user(firstname: str, lastname: str, email: str, username: str, google_id: str, accountcreatedtime: str):
    """Create a user that will authenticate via Google."""
    user_data = {
        "first_name": firstname,
        "last_name": lastname,
        "mail_id": email,
        "username": username,
        "google_id": google_id,
        "account_created_at": accountcreatedtime,
        "role": "user"
    }
    get_user_collection().insert_one(user_data)

def update_user_profile_photo(user_id, profile_photo):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.update_one(
        {"_id": user_id},
        {"$set": {"profile_photo": profile_photo}}
    )

def update_username(user_id, new_username):    
    get_user_collection().update_one(
        {"_id": user_id},
        {"$set": {"username": new_username}}
)
    
    
def update_email(user_id, new_email):
    get_user_collection().update_one(
        {"_id": user_id},    
        {"$set": {"mail_id": new_email}}
    )

def update_password(user_id, new_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    get_user_collection().update_one(
        {"_id": user_id},
        {"$set": {"password": hashed_password}}
    )
    
# Save image to MongoDB  
def save_image(username, filename, title, description, time_created,audio_filename=None,sentiment=None):
    image = {
        'username': username,
        'filename': filename,
        'title': title,
        'description': description,
        'created_at': time_created,
        'audio_filename': audio_filename,
        'sentiment': sentiment
    }
    get_image_collection().insert_one(image)

# Count all images from MongoDB
def total_images():
    return get_image_collection().count_documents({})

# Count all images from MongoDB uploaded today
def todays_images():
    last_24_hours = datetime.now() - timedelta(hours=24)
    recent_images_count = get_image_collection().count_documents({
    "created_at": {"$gte": last_24_hours}
    })
    return recent_images_count

def getallusers():
    users = get_user_collection().find()
    return users

def get_currentuser_from_session():
    user_data = session.get('user')
    if user_data is None:
        return None  
    
    user_id = user_data.get('user_id')  
    if not user_id:
        return None
    
    user = get_user_collection().find_one({'_id': user_id})
    return user

# Get all images from MongoDB
def get_images_by_user(username):
    images = get_image_collection().find({'username': username})
    return [{'id': str(image['_id']), 'filename': image['filename'], 'title': image['title'], 'description': image['description'], 'audio_filename': image.get('audio_filename', ""), 'sentiment':image.get('sentiment', "")} for image in images]

# Update image in MongoDB
def update_image(image_id, title, description):
    get_image_collection().update_one({'_id': image_id}, {'$set': {'title': title, 'description': description}})

# Delete image from MongoDB
def delete_image(image_id):
    get_image_collection().delete_one({'_id': image_id})

# Get image by id from MongoDB
def get_image_by_id(image_id):
    query = {'_id': image_id}
    image = get_image_collection().find_one(query)
    return image

def get_user_by_google_id(google_id):
    user_collection = DatabaseConfig.get_beehive_user_collection()
    return user_collection.find_one({"google_id": google_id})

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))
