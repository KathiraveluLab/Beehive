from flask import Blueprint, request, jsonify
import os
import requests
from database.admindatahandler import is_admin
from database.userdatahandler import get_images_by_user, get_recent_uploads, get_upload_stats
from utils.clerk_auth import require_auth

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Get all images uploaded by a user (admin access)
@admin_bp.route('/user_uploads/<user_id>')
@require_auth
def admin_user_images_show(user_id):
    try:
        images = get_images_by_user(user_id)
        return jsonify({
            'images': images
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# Get all users
@admin_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    try:
        # Get query parameters
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Get users from Clerk using REST API
        clerk_api_key = os.getenv('CLERK_SECRET_KEY')
        headers = {'Authorization': f'Bearer {clerk_api_key}'}
        params = {
            'limit': limit,
            'offset': offset,
            'query': query if query else None
        }
        response = requests.get('https://api.clerk.com/v1/users', headers=headers, params=params)
        
        if not response.ok:
            raise Exception(f"Clerk API error: {response.text}")
            
        users_data = response.json()
        
        # Transform user data
        transformed_users = []
        users_list = users_data  
        for user in users_list:
            email = user['email_addresses'][0]['email_address'] if user['email_addresses'] else None
            transformed_users.append({
                'id': user['id'],
                'name': f"{user['first_name']} {user['last_name']}".strip(),
                'email': email,
                'role': user['public_metadata'].get('role', 'user'),
                'lastActive': user['last_active_at'],
                'image': user['image_url'],
                'clerkId': user['id']
            })
            print(transformed_users)
        
        return jsonify({
            'users': transformed_users,
            'totalCount': len(users_list)  
        })
        
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

# Get only users (not admins)
@admin_bp.route('/users/only-users', methods=['GET'])
@require_auth
def get_only_users():
    try:
        # Get query parameters
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Get users from Clerk using REST API
        clerk_api_key = os.getenv('CLERK_SECRET_KEY')
        headers = {'Authorization': f'Bearer {clerk_api_key}'}
        params = {
            'limit': limit,
            'offset': offset,
            'query': query if query else None
        }
        response = requests.get('https://api.clerk.com/v1/users', headers=headers, params=params)
        
        if not response.ok:
            raise Exception(f"Clerk API error: {response.text}")
            
        users_data = response.json()
        
        # Transform user data, filter only users with role 'user'
        transformed_users = []
        users_list = users_data  
        for user in users_list:
            role = user['public_metadata'].get('role', 'user')
            if role != 'user':
                continue
            email = user['email_addresses'][0]['email_address'] if user['email_addresses'] else None
            transformed_users.append({
                'id': user['id'],
                'name': f"{user['first_name']} {user['last_name']}".strip(),
                'email': email,
                'role': role,
                'lastActive': user['last_active_at'],
                'image': user['image_url'],
                'clerkId': user['id']
            })
            # print(transformed_users)
        
        return jsonify({
            'users': transformed_users,
            'totalCount': len(transformed_users)  
        })
        
    except Exception as e:
        print(f"Error fetching only users: {str(e)}")
        return jsonify({'error': 'Failed to fetch only users'}), 500

# Get dashboard statistics and recent activity
@admin_bp.route('/dashboard', methods=['GET'])
@require_auth
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
        print(f"Error fetching dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500
