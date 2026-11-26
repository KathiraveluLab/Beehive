from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
import re
import bcrypt
from flask import session
from database import databaseConfig
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
        "created_at": datetime.now(timezone.utc),
        "last_active": datetime.now(timezone.utc)
    }

    return beehive_user_collection.insert_one(user).inserted_id
# updates the last_active time
def update_last_seen(user_id):
    try:
        beehive_user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_active": datetime.now(timezone.utc)}}
        )
    except Exception as e:
        logger.error(f"Failed to update last_active for user {user_id}: {e}")
# Get user by username from MongoDB
def get_user_by_username(username: str):
    query = {
        "username": username
    }
    user = beehive_user_collection.find_one(query)
    return user


def get_user_by_id(user_id: str):
    """Retrieve a user document by their MongoDB ObjectId string."""
    try:
        user = beehive_user_collection.find_one({"_id": ObjectId(user_id)})
        return user
    except InvalidId as e:
        logger.warning(f"Invalid user ID format: {user_id}. Error: {e}")
        return None
    except Exception as e:
        logger.warning(f"Could not retrieve user for id {user_id}: {e}")
        return None


# Save image to MongoDB
def save_image(id, filename, title, description, time_created, audio_filename=None, sentiment=None, thumbnail_filename=None):
    try:
        normalized_user_id = ObjectId(id)
    except (TypeError, ValueError):
        # Keep compatibility with non-ObjectId legacy user IDs
        normalized_user_id = id

    image = {
        'user_id': normalized_user_id,
        'filename': filename.lower() if filename else filename,
        'title': title,
        'description': description,
        'created_at': time_created,
        'audio_filename': audio_filename.lower() if audio_filename else audio_filename,
        'sentiment': sentiment,
        'thumbnail_filename': thumbnail_filename.lower() if thumbnail_filename else thumbnail_filename
    }
    beehive_image_collection.insert_one(image)
    update_last_seen(id)

def get_image_by_thumbnail(thumbnail_filename):
    # Extract the filename
    if thumbnail_filename.startswith("thumbnails/"):
        thumbnail_filename = thumbnail_filename.replace("thumbnails/", "")

    # Case insensitive matching for thumbnail filename - standardized to lowercase
    image = beehive_image_collection.find_one({
        'thumbnail_filename': thumbnail_filename.lower()
    })

    if image:
        return image

    # map to the original pdf filename in case if thumbnail not found
    base_name = thumbnail_filename.rsplit('.', 1)[0]
    return beehive_image_collection.find_one({
        'filename': f"{base_name.lower()}.pdf"
    })
    
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


def _parse_iso_date(date_string, field_name):
    """
    Helper function to parse ISO date string with timezone handling.
    
    Args:
        date_string: ISO format date string
        field_name: Name of the field for error messages
    
    Returns:
        datetime object with timezone awareness
    
    Raises:
        ValueError: If date format is invalid
    """
    try:
        # Handle both ISO format with timezone and simple date format
        parsed_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        # Ensure timezone awareness
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        return parsed_date
    except ValueError:
        raise ValueError(f"Invalid '{field_name}' date format: {date_string}. Expected ISO format.")


def _build_user_id_query(user_id):
    """
    Build a MongoDB query that supports both string and ObjectId user IDs.
    
    This helper ensures compatibility with legacy string-based user IDs while
    also supporting ObjectId formatted IDs, providing flexibility across the codebase.
    
    Args:
        user_id: User ID (can be string or ObjectId)
    
    Returns:
        dict: MongoDB query dictionary with '$in' operator for flexible user_id matching
    """
    user_id_candidates = {user_id}
    try:
        user_id_candidates.add(ObjectId(user_id))
    except (TypeError, ValueError):
        # Keep compatibility with legacy/non-ObjectId identifiers.
        pass
    
    return {'user_id': {'$in': list(user_id_candidates)}}


def search_and_filter_images(user_id, search_query=None, sentiment=None, from_date=None, to_date=None, 
                             sort_by='date', sort_order='desc', limit=12, offset=0):
    # Parse the dates first so a bad value raises ValueError for the route to turn into a 400,
    # instead of being swallowed below and shown as "no results".
    from_dt = _parse_iso_date(from_date, 'from') if from_date else None
    to_dt = _parse_iso_date(to_date, 'to') if to_date else None

    try:
        query = _build_user_id_query(user_id)
        update_last_seen(user_id)
        if search_query and search_query.strip():
            query['$text'] = {'$search': search_query.strip()}
        
        if sentiment and sentiment.strip():
            query['sentiment'] = sentiment.strip()
        
        if from_dt or to_dt:
            date_query = {}
            if from_dt:
                date_query['$gte'] = from_dt

            if to_dt:
                # Use the date as-is since frontend now sends with time
                date_query['$lte'] = to_dt
            
            if date_query:
                query['created_at'] = date_query
        
        # Determine sort field, direction, and projection
        # Always include projection when search_query is present for efficiency
        projection = {'score': {'$meta': 'textScore'}} if search_query and search_query.strip() else None
        
        if search_query and search_query.strip() and sort_by == 'relevance':
            sort_field = 'score'
            sort_direction = -1  # Sort by text score descending
        elif sort_by == 'title':
            sort_field = 'title'
            sort_direction = 1 if sort_order == 'asc' else -1
        else:
            sort_field = 'created_at'
            sort_direction = 1 if sort_order == 'asc' else -1
        
        total_count = beehive_image_collection.count_documents(query)
        
        # Build cursor with proper sort syntax
        if search_query and search_query.strip() and sort_by == 'relevance':
            # For text score sorting, use $meta in projection and sort by the projected field
            cursor = beehive_image_collection.find(query, projection).sort([('score', {'$meta': 'textScore'})])
        else:
            cursor = beehive_image_collection.find(query, projection).sort([(sort_field, sort_direction)])
        images = list(cursor.skip(offset).limit(limit))
        
        images_list = [{
            'id': str(image['_id']),
            'filename': image['filename'],
            'title': image['title'],
            'description': image['description'],
            'audio_filename': image.get('audio_filename', ''),
            'sentiment': image.get('sentiment', ''),
            'created_at': image['created_at']['$date'] if isinstance(image.get('created_at'), dict) else image.get('created_at')
        } for image in images]
        
        return {
            'images': images_list,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'hasMore': (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error in search_and_filter_images: {str(e)}")
        return {
            'images': [],
            'total': 0,
            'limit': limit,
            'offset': offset,
            'hasMore': False,
            'error': 'An unexpected error occurred while searching for images.'
        }


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
        
        # Build query using both string and ObjectId user ID forms for compatibility.
        query = _build_user_id_query(user_id)
        
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

def get_user_stats(user_id, trend_days=7):
    """
    Return upload statistics for a single user.

    Returns:
        dict with keys: total_uploads, voice_notes, sentiments (dict),
        daily_trend (list), last_upload_at (ISO string or None)
    """
    try:
        today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        trend_start = today_utc - timedelta(days=trend_days - 1)

        pipeline = [
            {"$match": _build_user_id_query(user_id)},
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "voice_notes": [
                        {"$match": {"audio_filename": {"$nin": [None, ""]}}},
                        {"$count": "count"},
                    ],
                    "sentiments": [
                        {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
                    ],
                    "daily_trend": [
                        {"$match": {"created_at": {"$gte": trend_start}}},
                        {
                            "$group": {
                                "_id": {
                                    "$dateToString": {
                                        "format": "%Y-%m-%d",
                                        "date": "$created_at",
                                    }
                                },
                                "count": {"$sum": 1},
                            }
                        },
                        {"$sort": {"_id": 1}},
                    ],
                    "last_upload": [
                        {"$sort": {"created_at": -1}},
                        {"$limit": 1},
                        {"$project": {"created_at": 1}},
                    ],
                }
            },
        ]

        result = list(beehive_image_collection.aggregate(pipeline))[0]

        # Sentiments map
        sentiment_counts = {
            item["_id"]: item["count"]
            for item in result.get("sentiments", [])
            if item.get("_id")
        }

        # Fill in every day of the trend window (even zero-upload days)
        upload_map = {item["_id"]: item["count"] for item in result.get("daily_trend", [])}
        daily_trend = []
        for i in range(trend_days):
            date_str = (trend_start + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_trend.append({"date": date_str, "count": upload_map.get(date_str, 0)})

        # Last upload timestamp
        last_upload_docs = result.get("last_upload", [])
        last_upload_at = None
        if last_upload_docs:
            ts = last_upload_docs[0].get("created_at")
            if ts:
                last_upload_at = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)

        return {
            "total_uploads": result["total"][0]["count"] if result.get("total") else 0,
            "voice_notes": result["voice_notes"][0]["count"] if result.get("voice_notes") else 0,
            "sentiments": {
                "positive": sentiment_counts.get("positive", 0),
                "negative": sentiment_counts.get("negative", 0),
                "neutral": sentiment_counts.get("neutral", 0),
            },
            "daily_trend": daily_trend,
            "last_upload_at": last_upload_at,
        }

    except Exception as e:
        logger.error(f"Error in get_user_stats for user {user_id}: {e}")
        return {
            "total_uploads": 0,
            "voice_notes": 0,
            "sentiments": {"positive": 0, "negative": 0, "neutral": 0},
            "daily_trend": [],
            "last_upload_at": None,
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
def get_recent_uploads(page=1, limit=10, username_filter=None, from_date=None, end_date=None, sort_method="date_desc"):
    try:
        offset = max(0, (page - 1)) * limit
        match_query = {}
        
        # Handle date range filtering
        created_at_query = {}
        if from_date:
            created_at_query["$gte"] = from_date
        if end_date:
            created_at_query["$lte"] = end_date
        if created_at_query:
            match_query["created_at"] = created_at_query

        # Handle username filter by finding IDs first (uses users collection indexes)
        if username_filter:
            matching_users = beehive_user_collection.find(
                {"username": {"$regex": re.escape(username_filter), "$options": "i"}},
                {"_id": 1}
            )
            user_ids = [u["_id"] for u in matching_users]
            # Match both string and ObjectId user_id formats for compatibility
            match_query["user_id"] = {"$in": user_ids + [str(uid) for uid in user_ids]}

        # Determine sort criteria
        sort_criteria = {"created_at": -1}
        if sort_method == "date_asc":
            sort_criteria = {"created_at": 1}
        elif sort_method == "user_asc":
            sort_criteria = {"username": 1, "created_at": -1}
        elif sort_method == "user_desc":
            sort_criteria = {"username": -1, "created_at": -1}

        # Build optimized data pipeline
        data_pipeline = []
        
        # If sorting by username, we must join BEFORE sorting
        if sort_method in ["user_asc", "user_desc"]:
            data_pipeline.extend([
                {
                    "$set": {
                        "user_id_obj": {
                            "$convert": {
                                "input": "$user_id",
                                "to": "objectId",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": beehive_user_collection.name,
                        "localField": "user_id_obj",
                        "foreignField": "_id",
                        "as": "user_mapping"
                    }
                },
                {"$set": {"user_mapping": {"$first": "$user_mapping"}}},
                {"$set": {"username": "$user_mapping.username"}},
                {"$sort": sort_criteria},
                {"$skip": offset},
                {"$limit": limit}
            ])
        else:
            # If sorting by date, we can paginate FIRST, then join only for the result set (much faster)
            data_pipeline.extend([
                {"$sort": sort_criteria},
                {"$skip": offset},
                {"$limit": limit},
                {
                    "$set": {
                        "user_id_obj": {
                            "$convert": {
                                "input": "$user_id",
                                "to": "objectId",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": beehive_user_collection.name,
                        "localField": "user_id_obj",
                        "foreignField": "_id",
                        "as": "user_mapping"
                    }
                },
                {"$set": {"user_mapping": {"$first": "$user_mapping"}}},
                {"$set": {"username": {"$ifNull": ["$user_mapping.username", "Unknown User"]}}},
            ])

        # Execute single aggregation with $facet for count + data
        pipeline = [
            {"$match": match_query},
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "data": data_pipeline
                }
            }
        ]

        result = list(beehive_image_collection.aggregate(pipeline))[0]
        total_count = result["total"][0]["count"] if result["total"] else 0
        uploads = result["data"]

        uploads_list = []
        for upload in uploads:
            user_id = upload.get('user_id')
            user_name = upload.get('username') or "Unknown User"
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
        return uploads_list, total_count
    except Exception as e:
        logger.error(f"Error getting recent uploads: {str(e)}")
        return [], 0

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


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def get_lock_status(user_id_or_doc, now=None):
    """Return lock info for a user: is_locked, remaining_seconds, failed_attempts.

    Accepts either a user ID (str or ObjectId) or an already-fetched user
    document (dict), avoiding a redundant DB query when the caller has the
    document in hand.  An optional ``now`` datetime can be injected for testing.
    """
    if isinstance(user_id_or_doc, dict):
        user = user_id_or_doc
    else:
        try:
            uid = user_id_or_doc if isinstance(user_id_or_doc, ObjectId) else ObjectId(user_id_or_doc)
        except (InvalidId, TypeError):
            return {"is_locked": False, "remaining_seconds": 0, "failed_attempts": 0}
        user = beehive_user_collection.find_one(
            {"_id": uid},
            {"failed_login_attempts": 1, "locked_until": 1}
        )

    if not user:
        return {"is_locked": False, "remaining_seconds": 0, "failed_attempts": 0}

    locked_until = user.get("locked_until")
    if now is None:
        now = datetime.now(timezone.utc)

    locked_until_aware = (
        locked_until if locked_until and locked_until.tzinfo is not None
        else locked_until.replace(tzinfo=timezone.utc) if locked_until
        else None
    )
    failed_attempts = user.get("failed_login_attempts", 0)
    if locked_until_aware and locked_until_aware > now:
        remaining = int((locked_until_aware - now).total_seconds() + 1)
        return {
            "is_locked": True,
            "remaining_seconds": remaining,
            "failed_attempts": failed_attempts,
        }
    return {"is_locked": False, "remaining_seconds": 0, "failed_attempts": failed_attempts}


def increment_failed_attempts(user_id):
    """Increment failed login counter; lock the account if threshold is reached.

    Returns the new failed attempt count.
    """
    try:
        uid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    except (InvalidId, TypeError):
        return 0

    result = beehive_user_collection.find_one_and_update(
        {"_id": uid},
        {"$inc": {"failed_login_attempts": 1}},
        return_document=True,
        projection={"failed_login_attempts": 1},
    )
    if not result:
        return 0

    new_count = result.get("failed_login_attempts", 0)
    if new_count >= MAX_FAILED_ATTEMPTS:
        locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        beehive_user_collection.update_one(
            {"_id": uid},
            {"$set": {"locked_until": locked_until}},
        )
    return new_count


def reset_failed_attempts(user_id):
    """Clear the failed login counter and any lockout on successful authentication."""
    try:
        uid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    except (InvalidId, TypeError):
        return

    beehive_user_collection.update_one(
        {"_id": uid},
        {"$unset": {"failed_login_attempts": "", "locked_until": ""}},
    )


def unlock_account(user_id):
    """Admin action: remove lockout and reset failed attempts. Returns True if user found."""
    try:
        uid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
    except (InvalidId, TypeError):
        return False

    result = beehive_user_collection.update_one(
        {"_id": uid},
        {"$unset": {"failed_login_attempts": "", "locked_until": ""}},
    )
    return result.matched_count > 0


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
def get_user_analytics():
    try:
        # Use calendar months for consistency and clarity
        today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_this_month = today_utc.replace(day=1)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)

        # Use a single aggregation pipeline for performance
        pipeline = [
            {
                '$facet': {
                    'total_users': [{'$match': {'role': 'user'}}, {'$count': 'count'}],
                    'new_users_this_month': [{'$match': {'role': 'user', 'created_at': {'$gte': start_of_this_month}}}, {'$count': 'count'}],
                    'active_users_this_month': [{'$match': {'role': 'user', 'last_active': {'$gte': start_of_this_month}}}, {'$count': 'count'}],
                    'active_users_last_month': [{'$match': {'role': 'user', 'last_active': {'$gte': start_of_last_month, '$lt': start_of_this_month}}}, {'$count': 'count'}]
                }
            }
        ]

        data = list(beehive_user_collection.aggregate(pipeline))[0]

        def _get_facet_count(results):
            return results[0].get('count', 0) if results else 0

        total_users = _get_facet_count(data.get('total_users'))
        new_users_count = _get_facet_count(data.get('new_users_this_month'))
        active_users_this_month = _get_facet_count(data.get('active_users_this_month'))
        active_users_last_month = _get_facet_count(data.get('active_users_last_month'))
        previous_total_users = total_users - new_users_count
        if previous_total_users == 0:
            increase = 100.0 if new_users_count > 0 else 0.0
        else:
            increase = (new_users_count / previous_total_users) * 100

        if active_users_last_month == 0:
            active_increase = 100.0 if active_users_this_month > 0 else 0.0
        else:
            active_increase = ((active_users_this_month - active_users_last_month) / active_users_last_month) * 100

        summary = {
            "users": {
                "total": total_users,
                "increase": round(increase, 2)
            },
            "activeUsers": {
                "total": active_users_this_month,
                "increase": round(active_increase, 2)
            },
            "timeframe": "This month"
        }
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        return None
    

# Get image record by its filename for ownership verification
def get_image_by_filename(filename):
    return beehive_image_collection.find_one({'filename': filename.lower()})