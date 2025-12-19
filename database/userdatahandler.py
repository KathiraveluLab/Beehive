from datetime import datetime, timedelta, timezone
# import re
# import bcrypt
from flask import session
from database import databaseConfig
import requests
import os

beehive_image_collection = databaseConfig.get_beehive_image_collection()
beehive_notification_collection = databaseConfig.get_beehive_notification_collection()
beehive_user_collection = databaseConfig.get_beehive_user_collection()

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

# Get paginated images (method)
def _get_paginated_images_by_user(user_id, page=1, page_size=12):
    
    try:
        skip = (page - 1) * page_size
        
        # total count 
        total_count = beehive_image_collection.count_documents({'user_id': user_id})
        
        # Get images
        images = list(beehive_image_collection.find({'user_id': user_id})
                      .sort('created_at', -1)
                      .skip(skip)
                      .limit(page_size))
        
        formatted_images = [{
            'id': str(image['_id']),
            'filename': image['filename'],
            'title': image['title'],
            'description': image['description'],
            'audio_filename': image.get('audio_filename', ""),
            'sentiment': image.get('sentiment', ""),
            'created_at': image['created_at']['$date'] if isinstance(image.get('created_at'), dict) else image.get('created_at')
        } for image in images]
        
        return {
            'images': formatted_images,
            'total_count': total_count,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total_count + page_size - 1) // page_size if page_size > 0 else 0
        }
    except Exception as e:
        print(f"Error getting paginated images: {str(e)}")
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
        recent_uploads = list(beehive_image_collection.find().sort(
            'created_at', -1).limit(limit))
        if not recent_uploads:
            return []

        user_ids = list({str(upload.get('user_id'))
                        for upload in recent_uploads if upload.get('user_id')})

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
        print(f"Error getting upload analytics: {e}")
        return None

def _fetch_clerk_users(params):
    headers = {'Authorization': f'Bearer {os.getenv("CLERK_SECRET_KEY")}'}
    all_users = []
    limit, offset = 200, 0

    # Use a session for connection reuse
    with requests.Session() as session:
        session.headers.update(headers)
        
        while True:
            paginated_params = {**params, 'limit': limit, 'offset': offset}
            response = session.get('https://api.clerk.com/v1/users', params=paginated_params)
            response.raise_for_status()
            users_page = response.json()
            if not users_page:
                break
            all_users.extend(users_page)
            offset += limit

    return all_users

def get_user_analytics(trend_days=7):
    try:
        # Date setup
        today_utc = datetime.now(timezone.utc)
        start_of_this_month = today_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        trend_start_date = today_utc.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=trend_days - 1)
        fetch_since_ms = int(start_of_last_month.timestamp() * 1000)
        
        # Fetch data once
        all_new_users = _fetch_clerk_users({'created_at_after': fetch_since_ms})
        all_active_users = _fetch_clerk_users({'last_sign_in_at_after': fetch_since_ms})
        
        count_response = requests.get('https://api.clerk.com/v1/users/count', headers={'Authorization': f'Bearer {os.getenv("CLERK_SECRET_KEY")}'})
        count_response.raise_for_status()
        overall_total_users = count_response.json().get('total_count', 0)

        # Process data for summary and trend
        new_this_month, new_last_month = 0, 0
        active_this_month, active_last_month, active_total_30_days = 0, 0, 0
        daily_new = { (trend_start_date + timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(trend_days) }
        daily_active = { (trend_start_date + timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(trend_days) }

        for user in all_new_users:
            created_at = datetime.fromtimestamp(user['created_at'] / 1000, tz=timezone.utc)
            if start_of_this_month <= created_at: new_this_month += 1
            elif start_of_last_month <= created_at: new_last_month += 1
            date_str = created_at.strftime('%Y-%m-%d')
            if date_str in daily_new: daily_new[date_str] += 1
        
        for user in all_active_users:
            last_sign_in_at = datetime.fromtimestamp(user['last_sign_in_at'] / 1000, tz=timezone.utc)
            if last_sign_in_at >= today_utc - timedelta(days=30): active_total_30_days += 1
            if start_of_this_month <= last_sign_in_at: active_this_month += 1
            elif start_of_last_month <= last_sign_in_at: active_last_month += 1
            date_str = last_sign_in_at.strftime('%Y-%m-%d')
            if date_str in daily_active: daily_active[date_str] += 1
        
        # Build summary
        new_increase = round(((new_this_month - new_last_month) / new_last_month) * 100, 2) if new_last_month > 0 else (100.0 if new_this_month > 0 else 0.0)
        active_increase = round(((active_this_month - active_last_month) / active_last_month) * 100, 2) if active_last_month > 0 else (100.0 if active_this_month > 0 else 0.0)
        summary = {
            'users': {'total': overall_total_users, 'increase': new_increase},
            'activeUsers': {'total': active_total_30_days, 'increase': active_increase},
            'timeframe': 'This month'
        }

        # Build trend
        trend, prev_new, prev_active = [], 0, 0
        for date_str in sorted(daily_new.keys()):
            new_count, active_count = daily_new[date_str], daily_active[date_str]
            new_inc = round(((new_count - prev_new) / prev_new) * 100, 2) if prev_new > 0 else (100.0 if new_count > 0 else 0.0)
            active_inc = round(((active_count - prev_active) / prev_active) * 100, 2) if prev_active > 0 else (100.0 if active_count > 0 else 0.0)
            trend.append({'date': date_str, 'users': {'total': new_count, 'increase': new_inc}, 'activeUsers': {'total': active_count, 'increase': active_inc}})
            prev_new, prev_active = new_count, active_count
        
        return {'summary': summary, 'trend': trend}

    except Exception as e:
        print(f"An error occurred in user analytics: {e}")
        return None