from datetime import datetime, timedelta
# import re
# import bcrypt
from flask import session
from Database import databaseConfig
import requests
import os

beehive_image_collection = databaseConfig.get_beehive_image_collection()
beehive_notification_collection = databaseConfig.get_beehive_notification_collection()

# Get user by username from MongoDB
def get_user_by_username(username: str):
    query = {
        "username" : username
    }
    user = beehive_user_collection.find_one(query)
    return user

    
# Save image to MongoDB  
def save_image(id, filename, title, description, time_created,audio_filename=None,sentiment=None):
    image = {
        'user_id': id,
        'filename': filename,
        'title': title,
        'description': description,
        'created_at': time_created,
        'audio_filename': audio_filename,
        'sentiment': sentiment
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
def get_images_by_user(user_id):
    images = beehive_image_collection.find({'user_id': user_id})
    return [{
        'id': str(image['_id']), 
        'filename': image['filename'], 
        'title': image['title'], 
        'description': image['description'], 
        'audio_filename': image.get('audio_filename', ""), 
        'sentiment': image.get('sentiment', ""),
        'created_at': image['created_at']['$date'] if isinstance(image.get('created_at'), dict) else image.get('created_at')
    } for image in images]

# Get images by sentiments list from MongoDB
def get_images_by_sentiments(username, sentiment_list, match_all):
    if match_all:
        # Match all tags (AND logic)
        query = {
            "username": username,
            "$and": [{"sentiment": {"$regex": tag, "$options": "i"}} for tag in sentiment_list]
        }
    else:
        # Match any tag (OR logic)
        query = {
            "username": username,
            "$or": [{"sentiment": {"$regex": tag, "$options": "i"}} for tag in sentiment_list]
        }

    images = beehive_image_collection.find(query)
    return [{'id': str(image['_id']), 
             'filename': image['filename'], 
             'title': image['title'], 
             'description': image['description'], 
             'audio_filename': image.get('audio_filename', ""), 
             'sentiment': image.get('sentiment', "")} for image in images]

# Update image in MongoDB
def update_image(image_id, title, description, sentiment=None):
    update_data = {
        'title': title, 
        'description': description
    }
    
    # Only include sentiment in the update if it is provided by the user
    if sentiment is not None:
        update_data['sentiment'] = sentiment
        
    beehive_image_collection.update_one(
        {'_id': image_id}, 
        {'$set': update_data}
    )

# Delete image from MongoDB
def delete_image(image_id):
    beehive_image_collection.delete_one({'_id': image_id})

# Get image by ID from MongoDB
def get_image_by_id(image_id):
    image = beehive_image_collection.find_one({'_id': image_id})
    return image

# Get upload statistics for admin dashboard
def get_upload_stats():
    """Get statistics for admin dashboard including total users, images, and voice notes."""
    try:
        # Count total images
        total_images = beehive_image_collection.count_documents({})
        
        # Count voice notes (images with audio_filename)
        total_voice_notes = beehive_image_collection.count_documents({
            "audio_filename": {"$exists": True, "$ne": None}
        })
        
        return {
            'totalImages': total_images,
            'totalVoiceNotes': total_voice_notes,
            'totalMedia': total_images + total_voice_notes
        }
    except Exception as e:
        print(f"Error getting upload stats: {str(e)}")
        return {
            'totalImages': 0,
            'totalVoiceNotes': 0,
            'totalMedia': 0
        }

# Get recent uploads for admin dashboard
def get_recent_uploads(limit=10):
    """Get recent uploads with user information from Clerk for admin dashboard."""
    try:
        #  Get recent uploads sorted by creation date
        recent_uploads = list(beehive_image_collection.find().sort('created_at', -1).limit(limit))
        if not recent_uploads:
            return []
        
        user_ids = list({str(upload.get('user_id')) for upload in recent_uploads if upload.get('user_id')})

        clerk_api_key = os.getenv('CLERK_SECRET_KEY')
        headers = {'Authorization': f'Bearer {clerk_api_key}'}

        response = requests.get(
            'http://127.0.0.1:5000/api/admin/users',
            headers=headers,
            params={'query': ','.join(user_ids), 'limit': len(user_ids)}
        )
        users_data = response.json().get('users', []) if response.ok else []
        # map of user_id to user info
        user_map = {user['id']: user for user in users_data}

        # uploads list with user info
        uploads_list = []
        for upload in recent_uploads:
            user_id = str(upload.get('user_id'))
            user = user_map.get(user_id)
            user_name = user['name'] if user else 'Unknown User'
            uploads_list.append({
                'id': str(upload['_id']),
                'title': upload.get('title', ''),
                'user': user_name,
                'user_id': user_id,
                'timestamp': upload['created_at']['$date'] if isinstance(upload.get('created_at'), dict) else upload.get('created_at'),
                'description': upload.get('description', ''),
                'filename': upload.get('filename', ''),
                'audio_filename': upload.get('audio_filename', ''),
                'sentiment': upload.get('sentiment', '')
            })
        return uploads_list
    except Exception as e:
        print(f"Error getting recent uploads: {str(e)}")
        return []

def save_notification(user_id, username, filename, title, time_created,sentiment):
            # Insert notification for admin
                notification = {
                    "type": "image_upload",
                    "user_id": user_id,
                    "username": username,
                    "image_filename": filename,
                    "title": title,
                    "timestamp": time_created,
                    "seen": False
                }
                beehive_notification_collection.insert_one(notification)    

def get_all_users():
    users = beehive_user_collection.find({}, {'_id': 1, 'username': 1})
    return list(users)    