from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
import re
import bcrypt
from flask import session
from database import databaseConfig
import requests
import os
from utils.logger import Logger

logger = Logger.get_logger("userdatahandler")

beehive_image_collection = databaseConfig.get_beehive_image_collection()
beehive_notification_collection = databaseConfig.get_beehive_notification_collection()
beehive_user_collection = databaseConfig.get_beehive_user_collection()
#create user in MongoDB
def create_user(username, email, password, role="user"):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }

    return beehive_user_collection.insert_one(user).inserted_id
# Get user by username from MongoDB
def get_user_by_username(username: str):
    query = {
        "username": username
    }
    user = beehive_user_collection.find_one(query)
    return user


# Save image to MongoDB
def save_image(id, filename, title, description, time_created, audio_filename=None, sentiment=None):
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
def get_images_by_user(user_id, limit=None, offset=None):
    """
    Return a list of images for a user, sorted by `created_at` in descending order.
    If `offset` and/or `limit` are provided, apply pagination using skip/limit on that
    sorted result set.
    """
    cursor = beehive_image_collection.find({'user_id': user_id}).sort('created_at', -1)
    if offset is not None:
        try:
            cursor = cursor.skip(int(offset))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid offset value: {offset}. Error: {e}")
    if limit is not None:
        try:
            cursor = cursor.limit(int(limit))
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid limit value: {limit}. Error: {e}")

    return [{
        'id': str(image['_id']),
        'filename': image.get('filename', ''),
        'title': image.get('title', ''),
        'description': image.get('description', ''),
        'audio_filename': image.get('audio_filename', ""),
        'sentiment': image.get('sentiment', ""),
        'created_at': image.get('created_at').get('$date') if isinstance(image.get('created_at'), dict) else image.get('created_at')
    } for image in cursor]

def count_images_by_user(user_id):
    try:
        return beehive_image_collection.count_documents({'user_id': user_id})
    except Exception as e:
        logger.error(f"Error counting images for user {user_id}: {e}")
        return 0

# Get paginated images (method)
def _get_paginated_images_by_user(user_id, page=1, page_size=12, filters=None):
    """
    Get paginated images for a user with optional filters and safe data access.
    
    Args:
        user_id: The user's ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        filters: Dictionary of filters - can contain:
            - 'q': search query (matches title or description)
            - 'sentiment': sentiment filter
            - 'date_filter': 'week', 'month', or 'custom'
            - 'from': custom start date (ISO string)
            - 'to': custom end date (ISO string)
    """
    try:
        # Calculate skip for pagination
        skip = (page - 1) * page_size
        
        # Build query
        query = {'user_id': user_id}
        
        # Apply filters if provided
        if filters:
            # Search query filter
            if filters.get('q'):
                search_query = re.escape(filters['q'])
                query['$or'] = [
                    {'title': {'$regex': search_query, '$options': 'i'}},
                    {'description': {'$regex': search_query, '$options': 'i'}}
                ]
            
            # Sentiment filter
            if filters.get('sentiment') and filters['sentiment'] != 'all':
                query['sentiment'] = filters['sentiment']
            
            # Date filter
            date_filter = filters.get('date_filter')
            if date_filter and date_filter != 'all':
                now = datetime.utcnow()
                if date_filter == 'week':
                    start_date = now - timedelta(days=7)
                    query['created_at'] = {'$gte': start_date}
                elif date_filter == 'month':
                    start_date = now - timedelta(days=30)
                    query['created_at'] = {'$gte': start_date}
                elif date_filter == 'custom':
                    date_range = {}
                    if filters.get('from'):
                        try:
                            from_date = datetime.fromisoformat(filters['from'].replace('Z', '+00:00'))
                            date_range['$gte'] = from_date
                        except (ValueError, AttributeError):
                            logger.warning(f"Invalid 'from' date format: {filters.get('from')}")
                    if filters.get('to'):
                        try:
                            to_date = datetime.fromisoformat(filters['to'].replace('Z', '+00:00'))
                            # Add one day to include the entire 'to' date
                            to_date = to_date + timedelta(days=1)
                            date_range['$lt'] = to_date
                        except (ValueError, AttributeError):
                            logger.warning(f"Invalid 'to' date format: {filters.get('to')}")
                    if date_range:
                        query['created_at'] = date_range
        
        # total count with filters applied
        total_count = beehive_image_collection.count_documents(query)
        
        # Get images
        images = list(beehive_image_collection.find(query)
                      .sort('created_at', -1)
                      .skip(skip)
                      .limit(page_size))
        
        # Use safe .get() access to prevent KeyError exceptions
        formatted_images = [{
            'id': str(image['_id']),
            'filename': image.get('filename', ''),
            'title': image.get('title', ''),
            'description': image.get('description', ''),
            'audio_filename': image.get('audio_filename', ""),
            'sentiment': image.get('sentiment', ""),
            'created_at': image.get('created_at').get('$date') if isinstance(image.get('created_at'), dict) else image.get('created_at')
        } for image in images]
        
        return {
            'images': formatted_images,
            'total_count': total_count,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total_count + page_size - 1) // page_size if page_size > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting paginated images: {str(e)}")
        return {
            'images': [],
            'total_count': 0,
            'page': page,
            'pageSize': page_size,
            'totalPages': 0
        }

# Get images by sentiments list from MongoDB ( Route to be used with the dreams prototype for analysis page)
# def get_images_by_sentiments(username, sentiment_list, match_all):
#     if match_all:
#         # Match all tags (AND logic)
#         query = {
#             "username": username,
#             "$and": [{"sentiment": {"$regex": tag, "$options": "i"}} for tag in sentiment_list]
#         }
#     else:
#         # Match any tag (OR logic)
#         query = {
#             "username": username,
#             "$or": [{"sentiment": {"$regex": tag, "$options": "i"}} for tag in sentiment_list]
#         }

#     images = beehive_image_collection.find(query)
#     return [{'id': str(image['_id']),
#              'filename': image['filename'],
#              'title': image['title'],
#              'description': image['description'],
#              'audio_filename': image.get('audio_filename', ""),
#              'sentiment': image.get('sentiment', "")} for image in images]

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

# Get image by audio filename from MongoDB
def get_image_by_audio_filename(audio_filename):
    """Get image record by its audio filename for ownership verification."""
    image = beehive_image_collection.find_one({'audio_filename': audio_filename})
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
        logger.error(f"Error getting upload stats: {str(e)}")
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
        recent_uploads = list(beehive_image_collection.find().sort(
            'created_at', -1).limit(limit))
        if not recent_uploads:
            return []
        # collect user ids and query local user collection
        raw_ids = [upload.get('user_id') for upload in recent_uploads if upload.get('user_id')]
        object_ids = []
        for uid in raw_ids:
            try:
                object_ids.append(ObjectId(uid))
            except Exception:
                # skip invalid ids
                continue

        users_cursor = beehive_user_collection.find({'_id': {'$in': object_ids}}) if object_ids else []
        users_data = {str(u['_id']): u for u in users_cursor}

        uploads_list = []
        for upload in recent_uploads:
            user_id = upload.get('user_id')
            user = users_data.get(str(user_id)) if user_id else None
            user_name = user.get('username') if user else 'Unknown User'
            uploads_list.append({
                'id': str(upload['_id']),
                'title': upload.get('title', ''),
                'user': user_name,
                'user_id': str(user_id) if user_id else None,
                'timestamp': upload['created_at']['$date'] if isinstance(upload.get('created_at'), dict) else upload.get('created_at'),
                'description': upload.get('description', ''),
                'filename': upload.get('filename', ''),
                'audio_filename': upload.get('audio_filename', ''),
                'sentiment': upload.get('sentiment', '')
            })
        return uploads_list
    except Exception as e:
        logger.error(f"Error getting recent uploads: {str(e)}")
        return []


def save_notification(user_id, username, filename, title, time_created, sentiment):
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

def get_upload_analytics(trend_days=7):
    try:
        # Date setup
        today_utc = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_this_month = today_utc.replace(day=1)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        trend_start_date = today_utc - timedelta(days=trend_days - 1)

        # Pipeline
        pipeline = [
            {
                '$facet': {
                    'sentiments': [{'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}}],
                    'content_types': [{'$group': {'_id': '$filetype', 'count': {'$sum': 1}}}],
                    'voice_notes': [{'$match': {'audio_filename': {'$ne': None}}}, {'$count': 'count'}],
                    'total_uploads': [{'$count': 'count'}],
                    'this_month_uploads': [
                        {'$match': {'created_at': {'$gte': start_of_this_month}}},
                        {'$count': 'count'}
                    ],
                    'last_month_uploads': [
                        {'$match': {'created_at': {'$gte': start_of_last_month, '$lt': start_of_this_month}}},
                        {'$count': 'count'}
                    ],
                    'daily_trend': [
                        {'$match': {'created_at': {'$gte': trend_start_date}}},
                        {'$group': {
                            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at', 'timezone': 'UTC'}},
                            'count': {'$sum': 1}
                        }},
                        {'$sort': {'_id': 1}}
                    ]
                }
            }
        ]
        
        # Execute and process query
        result = list(beehive_image_collection.aggregate(pipeline))[0]
        
        # Access results directly from the 'result' object.
        this_month_count = result['this_month_uploads'][0]['count'] if result['this_month_uploads'] else 0
        last_month_count = result['last_month_uploads'][0]['count'] if result['last_month_uploads'] else 0
        increase_perc = (
            round(((this_month_count - last_month_count) / last_month_count) * 100, 2)
            if last_month_count > 0 else (100.0 if this_month_count > 0 else 0.0)
        )
        sentiment_counts = {item['_id']: item['count'] for item in result.get('sentiments', []) if item.get('_id')}
        known_sentiments = {'positive', 'negative', 'neutral'}
        
        summary = {
            'total': result['total_uploads'][0]['count'] if result['total_uploads'] else 0,
            'voiceNotes': result['voice_notes'][0]['count'] if result['voice_notes'] else 0,
            'increase': increase_perc,
            'timeframe': 'This month',
            'sentimentAnalysis': {
                'positive': sentiment_counts.get('positive', 0),
                'negative': sentiment_counts.get('negative', 0),
                'neutral': sentiment_counts.get('neutral', 0),
                'custom': sum(count for sentiment, count in sentiment_counts.items() if sentiment not in known_sentiments)
            }
        }
        
        # Process trend
        upload_map = {item['_id']: item['count'] for item in result['daily_trend']}
        trend, prev_count = [], 0
        for i in range(trend_days):
            date_str = (trend_start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            count = upload_map.get(date_str, 0)
            increase = round(((count - prev_count) / prev_count) * 100, 2) if prev_count > 0 else (100.0 if count > 0 else 0.0)
            trend.append({'date': date_str, 'uploads': {'total': count, 'increase': increase}})
            prev_count = count

        return {'summary': summary, 'trend': trend}

    except Exception as e:
        logger.error(f"Error getting upload analytics: {e}")
        return None
