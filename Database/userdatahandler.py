from datetime import datetime, timedelta
import re
import bcrypt
from flask import session
from Database import DatabaseConfig


beehive_user_collection = DatabaseConfig.get_beehive_user_collection()
beehive_image_collection = DatabaseConfig.get_beehive_image_collection()

# Create user in MongoDB
def create_user(firstname: str, lastname: str, email: str, username: str, password: str, security_question: str, security_answer: str, accountcreatedtime: datetime):
    
    # Hash the password before storing
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_answer = bcrypt.hashpw(security_answer.encode('utf-8'), salt)
    user_data = {
        "first_name" : firstname,
        "last_name" : lastname,
        "mail_id" : email,
        "username" : username,
        "password" : hashed_password,
        "security_question": security_question,
        "security_answer": hashed_answer,  
        "account_created_at" : accountcreatedtime,
        "role" : "user"
    }
    user_inserted_id = beehive_user_collection.insert_one(user_data).inserted_id

# Check if username is available in MongoDB for registration purpose
def is_username_available(username: str):
    query = {
        "username" : username
    }

    count = beehive_user_collection.count_documents(query)
    return count == 0

def is_email_available(email: str):
    query = {
        "mail_id" : email
    }

    count = beehive_user_collection.count_documents(query)
    return count == 0

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
    user = beehive_user_collection.find_one(query)
    if user:
        return user.get("password")
    else:
        return None
    
# Get user by username from MongoDB
def get_user_by_username(username: str):
    query = {
        "username" : username
    }
    user = beehive_user_collection.find_one(query)
    return user

def get_user_by_email(email: str):
    """Get user by email from MongoDB."""
    query = {
        "mail_id": email
    }
    user = beehive_user_collection.find_one(query)
    return user

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
    user_inserted_id = beehive_user_collection.insert_one(user_data).inserted_id
    return user_inserted_id

def update_profile_photo(username, filename):
    """Update the profile photo filename for a user."""
    beehive_user_collection.update_one(
        {"username": username},
        {"$set": {"profile_photo": filename}}
    )

def update_username(user_id, new_username):    
    beehive_user_collection.update_one(
        {"_id": user_id},
        {"$set": {"username": new_username}}
)
    
    
def update_email(user_id, new_email):
    beehive_user_collection.update_one(
        {"_id": user_id},    
        {"$set": {"mail_id": new_email}}
    )

def update_password(user_id, new_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    beehive_user_collection.update_one(
        {"_id": user_id},
        {"$set": {"password": hashed_password}}
    )
    
# Save image to MongoDB  
def save_image(username, filename, title, description, time_created,audio_filename=None,sentiment=None, tags=None):
    image = {
        'username': username,
        'filename': filename,
        'title': title,
        'description': description,
        'created_at': time_created,
        'audio_filename': audio_filename,
        'sentiment': sentiment,
        'tags': tags
    }
    beehive_image_collection.insert_one(image)

# Count all images from MongoDB
def total_images():
    return beehive_image_collection.count_documents({})

# Count all images from MongoDB uploaded today
def todays_images():
    last_24_hours = datetime.now() - timedelta(hours=24)
    recent_images_count = beehive_image_collection.count_documents({
    "created_at": {"$gte": last_24_hours}
    })
    return recent_images_count

def getallusers():
    users = beehive_user_collection.find()
    return users

def get_currentuser_from_session():
    user_data = session.get('user')
    if user_data is None:
        return None  
    
    user_id = user_data.get('user_id')  
    if not user_id:
        return None
    
    user = beehive_user_collection.find_one({'_id': user_id})
    return user

# Get all images from MongoDB
def get_images_by_user(username):
    images = beehive_image_collection.find({'username': username})
def get_images_by_user(username):
    images = beehive_image_collection.find({'username': username})
    return [{'id': str(image['_id']), 
             'filename': image['filename'], 
             'title': image['title'], 
             'description': image['description'], 
             'audio_filename': image.get('audio_filename', ""), 
             'sentiment': image.get('sentiment', ""), 
             'tags': image.get('tags', "")} for image in images]
# Update image in MongoDB
def update_image(image_id, title, description):
    beehive_image_collection.update_one({'_id': image_id}, {'$set': {'title': title, 'description': description}})

# Delete image from MongoDB
def delete_image(image_id):
    beehive_image_collection.delete_one({'_id': image_id})

# Get image by id from MongoDB
def get_image_by_id(image_id):
    query = {'_id': image_id}
    image = beehive_image_collection.find_one(query)
    return image

def get_images_by_tags(username, tags, match_all):

    if match_all:
        # Match all tags (AND logic)
        query = {
            "username": username,
            "tags": {"$all": tags}
        }
    else:
        # Match any tag (OR logic)
        query = {
            "username": username,
            "tags": {"$in": tags}  
        }

    images = beehive_image_collection.find(query)
    return [{'id': str(image['_id']), 
             'filename': image['filename'], 
             'title': image['title'], 
             'description': image['description'], 
             'audio_filename': image.get('audio_filename', ""), 
             'sentiment': image.get('sentiment', ""), 
             'tags': image.get('tags', "")} for image in images]
