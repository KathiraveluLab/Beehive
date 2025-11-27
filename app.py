import base64
import os
from functools import wraps
import json
import datetime
import pathlib
import re
import sys
import logging
import magic
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_cors import CORS
from bson import ObjectId
from google_auth_oauthlib.flow import Flow
from bson.errors import InvalidId
import requests
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol
from database import userdatahandler
from werkzeug.utils import secure_filename
import fitz  
from PIL import Image
import bcrypt
from datetime import timedelta
import google.generativeai as genai
import traceback 


from database.admindatahandler import  is_admin
from database.userdatahandler import ( 
    delete_image,
    get_image_by_id,
    get_images_by_user,
    get_user_by_username, 
    save_image, 
    update_image,
    save_notification,
    get_all_users
)
from database.databaseConfig import get_beehive_notification_collection, get_beehive_message_collection
from utils.clerk_auth import require_auth

from decorators import login_is_required, require_admin_role

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from oauth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID

ALLOWED_EXTENSIONS = {'jpg','jpeg','png','gif','webp','heif','pdf','avif'}

ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'image/heif', 'application/pdf', 'image/avif'
}

# Initialized global MIME detector
try:
    MAGIC = magic.Magic(mime=True)
except Exception:
    MAGIC = None

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})  # Enable CORS for all routes with specific configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
# SECURITY FIX: Use environment variable for secret key
app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key or len(app.secret_key) < 32 or app.secret_key in {'beehive', 'beehive-secret-key'}:
    raise ValueError('CRITICAL: Set a secure FLASK_SECRET_KEY (at least 32 characters) in the environment!')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_THUMBNAIL_FOLDER'] = 'static/uploads/thumbnails/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/admin/login/callback"
)
    
# Upload images 
# Upload images 
@app.route('/api/user/upload/<user_id>', methods=['POST'])
def upload_images(user_id):
    try:
        # Check if files exist (support both single 'file' and multiple 'files')
        files_list = request.files.getlist('files') if 'files' in request.files else []
        if not files_list and 'file' in request.files:
            files_list = [request.files['file']]
        
        if not files_list:
            return jsonify({'error': 'No file provided'}), 400
        
        uploaded_files = []
        
        # Process each file
        for file in files_list:
            if file.filename == '':
                continue  # Skip empty files
            
            # SECURITY: Validate file extension
            if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                return jsonify({'error': f'File type not allowed: {file.filename}'}), 400
            
            # Get form data
            title = request.form.get('title', '')
            description = request.form.get('description', '')
            sentiment = request.form.get('sentiment', '')
            
            # Handle voice note if present (only for first file)
            voice_note_data = None
            if 'voice_note' in request.files and len(uploaded_files) == 0:
                voice_note = request.files['voice_note']
                if voice_note.filename:
                    voice_note_filename = secure_filename(f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{voice_note.filename}")
                    voice_note_path = os.path.join(app.config['UPLOAD_FOLDER'], voice_note_filename)
                    voice_note.save(voice_note_path)
                    voice_note_data = voice_note_filename
            
            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Generate thumbnail for PDFs
            thumbnail_path = None
            if filename.lower().endswith('.pdf'):
                thumbnail_path = generate_pdf_thumbnail(file_path, filename)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Save to database
            image_id = save_image(
                id=user_id,
                filename=filename,
                title=title,
                description=description,
                time_created=datetime.utcnow(),
                audio_filename=voice_note_data,
                sentiment=sentiment
            )
            
            # Save notification (FIX #2: Use 'timestamp' not 'created_at')
            save_notification(
                user_id=user_id,
                username=user_id,
                filename=filename,
                title=title,
                time_created=datetime.utcnow(),
                sentiment=sentiment,
                description=description,
                file_size=file_size,
                file_path=file_path
            )
            
            uploaded_files.append({
                'filename': filename,
                'image_id': str(image_id)
            })
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        }), 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# generate thumbnail for the pdf
def generate_pdf_thumbnail(pdf_path, filename):
    """Generate an image from the first page of a PDF using PyMuPDF."""
    # Ensure the thumbnails directory exists
    thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True) 

    pdf_document = fitz.open(pdf_path)
    
    #select only the first page for the thumbnail
    first_page = pdf_document.load_page(0)
    
    zoom = 2  # Increase for higher resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = first_page.get_pixmap(matrix=mat)
    
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    thumbnail_filename = filename.replace('.pdf', '.jpg')
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    image.save(thumbnail_path, 'JPEG')
    
    return thumbnail_path

# Edit images uploaded by the user
@app.route('/edit/<image_id>', methods=['PATCH'])
@require_auth
def edit_image(image_id):
    try:
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        sentiment = request.form.get('sentiment', '')

        if not title or not description:
            return jsonify({'error': 'Title and description are required.'}), 400

        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            return jsonify({'error': f'Invalid image ID format: {str(e)}'}), 400

        # Verify the image exists
        image = get_image_by_id(image_id)
        if not image:
            return jsonify({'error': 'Image not found.'}), 404
        # verify the ownership
        current_user_id = request.current_user['id']
        image_owner_id = image['user_id']

        if current_user_id != image_owner_id:
            return jsonify({'error': 'Unauthorized: You do not own this image.'}), 403
        
        # Update the image
        update_image(image_id, title, description, sentiment)
        return jsonify({'message': 'Image updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': f'Error updating image: {str(e)}'}), 500

@app.route('/audio/<filename>')
@require_auth
def serve_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
   
# Delete images uploaded by the user
@app.route('/delete/<image_id>', methods=['DELETE'])
@require_auth
def delete_image_route(image_id):
    try:
        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            return jsonify({'error': f'Invalid image ID format: {str(e)}'}), 400

        # Verify the image exists
        image = get_image_by_id(image_id)
        if not image:
            return jsonify({'error': 'Image not found.'}), 404
        #verify the ownership of user
        current_user_id = str(request.current_user.get('id'))
        image_owner_id = str(image.get('user_id'))

        if current_user_id != image_owner_id:
            return jsonify({'error': 'Unauthorized: You do not own this image.'}), 403
        
        # Delete image file from upload directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
            # Also delete thumbnail if it exists
            if image['filename'].lower().endswith('.pdf'):
                thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', 
                                            image['filename'].replace('.pdf', '.jpg'))
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

        # Delete audio file if it exists
        if image.get('audio_filename'):
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], image['audio_filename'])
            if os.path.exists(audio_path):
                os.remove(audio_path)

        # Delete image record from database
        delete_image(image_id)
        return jsonify({'message': 'Image deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': f'Error deleting image: {str(e)}'}), 500

# Get all images uploaded by a user
@app.route('/api/user/user_uploads')
@require_auth
def user_images_show():
    try:
        user_id = request.current_user['id']
        images = get_images_by_user(user_id)
        images_list = list(images) if images else []        
        response_data = {
            'images': images_list,
            'user_id': user_id,
            'message': 'Success'
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/admin/notifications', methods=['GET'])
@require_auth
def get_admin_notifications():
    try:
        notification_collection = get_beehive_notification_collection()

        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("limit", 5))
        except ValueError:
            return jsonify({"error": "Invalid 'page' or 'limit' parameter. Must be an integer."}), 400
        skip = (page - 1) * per_page

        # Count unseen notifications
        unseen_count = notification_collection.count_documents({"seen": False})

        notifications = list(
            notification_collection.find({})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(per_page)
        )

        for n in notifications:
            n["_id"] = str(n["_id"])
            if "timestamp" in n:
                n["timestamp"] = n["timestamp"].isoformat()

        return jsonify({
            "notifications": notifications,
            "unseen_count": unseen_count,
            "page": page
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/notifications/<user_id>', methods=['GET'])
 @require_auth
def get_user_notifications(user_id):
    """Get all notifications for a specific user"""
    try:
        notification_collection = get_beehive_notification_collection()
        
        # Get notifications for this user
        notifications = list(notification_collection.find({
            'user_id': user_id
        }).sort('created_at', -1).limit(50))
        
        # Format response - INCLUDE DETAILS!
        formatted_notifications = []
        for notif in notifications:
           formatted_notifications.append({
    'id': str(notif['_id']),
    'type': notif.get('type', 'info'),
    'message': notif.get('message', ''),
    'details': notif.get('details', {}),
    'is_read': notif.get('is_read', False),
    'created_at': notif.get('timestamp').isoformat() if notif.get('timestamp') else None  # ✅ CORRECT
})
        
        return jsonify({
            'success': True,
            'notifications': formatted_notifications
        }), 200
        
    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/send', methods=['POST'])
@require_auth
def send_chat_message():
    try:
        data = request.json
        from_id = request.current_user['id']
        from_role = request.current_user['role']
        to_id = data.get('to_id')
        to_role = data.get('to_role')
        content = data.get('content')
        timestamp = datetime.now()
        if not (from_id and from_role and to_id and to_role and content):
            return jsonify({'error': 'Missing required fields'}), 400
        message = {
            'from_id': from_id,
            'from_role': from_role,
            'to_id': to_id,
            'to_role': to_role,
            'content': content,
            'timestamp': timestamp
        }
        messages_col = get_beehive_message_collection()
        messages_col.insert_one(message)
        return jsonify({'message': 'Message sent'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/messages', methods=['GET'])
@require_auth
def get_chat_messages():
    try:
        current_user = request.current_user
        
        if current_user.get('role') == 'admin':
            # If the requester is an admin, they can specify a user_id
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'error': 'user_id is required'}), 400
        else:
            # We'll be ignoring any user_id passed in the query to prevent data leakage.
            user_id = current_user['id']

        messages_col = get_beehive_message_collection()
        # Get messages between this user and admin
        query = {
            '$or': [
                {'from_id': user_id, 'to_role': 'admin'},
                {'to_id': user_id, 'from_role': 'admin'}
            ]
        }
        messages = list(messages_col.find(query).sort('timestamp', 1))
        for m in messages:
            m['_id'] = str(m['_id'])
            if 'timestamp' in m:
                m['timestamp'] = m['timestamp'].isoformat()
        return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Import blueprints
from routes.adminroutes import admin_bp
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)