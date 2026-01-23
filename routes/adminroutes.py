from flask import Blueprint, request, jsonify
import os
import requests
from decorators import require_admin_role
from database.userdatahandler import get_images_by_user, _get_paginated_images_by_user, get_recent_uploads, get_upload_stats, get_upload_analytics, get_user_analytics
from utils.logger import Logger
from utils.sanitize import sanitize_api_query

logger = Logger.get_logger("adminroutes")
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Helper function to fetch all users from Clerk to handle pagination limits
def _fetch_all_clerk_users(api_key): 
    all_users = []
    limit = 100 # Fetch in batches of 100
    offset = 0
    
    while True:
        headers = {'Authorization': f'Bearer {api_key}'}
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get('https://api.clerk.com/v1/users', headers=headers, params=params)
        
        if not response.ok:
            raise Exception(f"Clerk API error: {response.text}")
            
        batch = response.json()
        all_users.extend(batch)
        
        if len(batch) < limit:
            break
        
        offset += limit
        
    return all_users

# Get all images uploaded by a user (admin access)
@admin_bp.route('/user_uploads/<user_id>')
@require_admin_role
def admin_user_images_show(user_id):
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 12))
        
        # Validate pagination parameters
        page = max(1, page)
        page_size = min(max(1, page_size), 50)
        
        result = _get_paginated_images_by_user(user_id, page, page_size)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching user uploads", exc_info=True)
        return jsonify({'error': 'Failed to fetch user uploads'}), 500

# Get all users
@admin_bp.route('/users', methods=['GET'])
@require_admin_role
def get_users():
    try:
        # Get query parameters
        query = sanitize_api_query(request.args.get('query', '')).lower()
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        clerk_api_key = os.getenv('CLERK_SECRET_KEY')
        if not clerk_api_key:
            logger.error("CLERK_SECRET_KEY is not set")
            return jsonify({'error': 'Server configuration error'}), 500

        # Fetch ALL users first to ensure complete dataset
        users_list = _fetch_all_clerk_users(clerk_api_key)
        
        # Transform and Filter
        transformed_users = []
        
        for user in users_list:
            # Using public_metadata instead of unsafe_metadata for security
            role = user['public_metadata'].get('role', 'user')
            first_name = user.get('first_name') or ""
            last_name = user.get('last_name') or ""
            full_name = f"{first_name} {last_name}".strip()
            email = user['email_addresses'][0]['email_address'] if user['email_addresses'] else ""
            
            # Apply search query locally
            if query:
                if query not in full_name.lower() and query not in email.lower():
                    continue

            transformed_users.append({
                'id': user['id'],
                'name': full_name,
                'email': email,
                'role': role, 
                'lastActive': user['last_active_at'],
                'image': user['image_url'],
                'clerkId': user['id']
            })
        
        #  Apply pagination in-memory on the complete list
        total_count = len(transformed_users)
        paginated_users = transformed_users[offset : offset + limit]
        
        return jsonify({
            'users': paginated_users,
            'totalCount': total_count
        })
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Failed to fetch users. Please try again.'}), 500

# Get only users (not admins)
@admin_bp.route('/users/only-users', methods=['GET'])
@require_admin_role
def get_only_users():
    try:
        # Get query parameters
        query = sanitize_api_query(request.args.get('query', '')).lower()
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        clerk_api_key = os.getenv('CLERK_SECRET_KEY')
        if not clerk_api_key:
            logger.error("CLERK_SECRET_KEY is not set")
            return jsonify({'error': 'Server configuration error'}), 500
    
        users_list = _fetch_all_clerk_users(clerk_api_key)
        
        # Transform and Filter
        transformed_users = []
        for user in users_list:
            role = user['public_metadata'].get('role', 'user')
            
            # Filter only users (role == 'user')
            if role != 'user':
                continue
                
            first_name = user.get('first_name') or ""
            last_name = user.get('last_name') or ""
            full_name = f"{first_name} {last_name}".strip()
            email = user['email_addresses'][0]['email_address'] if user['email_addresses'] else ""

            # Apply search query locally
            if query:
                if query not in full_name.lower() and query not in email.lower():
                    continue

            transformed_users.append({
                'id': user['id'],
                'name': full_name,
                'email': email,
                'role': role,
                'lastActive': user['last_active_at'],
                'image': user['image_url'],
                'clerkId': user['id']
            })
    
        total_count = len(transformed_users)
        paginated_users = transformed_users[offset : offset + limit]
        
        return jsonify({
            'users': paginated_users,
            'totalCount': total_count
        })
        
    except Exception as e:
        logger.error(f"Error fetching only users: {str(e)}")
        return jsonify({'error': 'Failed to fetch users. Please try again.'}), 500

# Get dashboard statistics and recent activity
@admin_bp.route('/dashboard', methods=['GET'])
@require_admin_role
def get_dashboard_data():
    try:
        # Get query parameters for recent activity
        limit = int(request.args.get('limit', 10))
        
        # Get statistics
        stats = get_upload_stats()
        
        # Get recent uploads
        recent_uploads = get_recent_uploads(limit)
        
        return jsonify({
            'stats': stats,
            'recentUploads': recent_uploads
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data. Please try again.'}), 500
    

@admin_bp.route('/analytics', methods=['GET'])
@require_admin_role
def get_all_analytics():
    try:
        days_ago = 7

        upload_data = get_upload_analytics(trend_days=days_ago)
        user_data = get_user_analytics(trend_days=days_ago)

        if not upload_data or not user_data:
            return jsonify({"error": "Failed to retrieve analytics data"}), 500

        combined_data = {
            "uploads": upload_data,
            "users": user_data
        }

        return jsonify(combined_data), 200

    except Exception as e:
        logger.error(f"Error fetching combined analytics: {str(e)}")
        return jsonify({"error": "Failed to fetch analytics data. Please try again."}), 500
