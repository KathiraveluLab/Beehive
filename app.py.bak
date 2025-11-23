import base64
from functools import wraps
import json
import os
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
app.secret_key = 'beehive'
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
@app.route('/api/user/upload', methods=['POST'])
@require_auth
def upload_images():
    user_id = request.current_user['id']
    try:
        username = request.form.get('username', '')
        files = request.files.getlist('files')  # Supports multiple file uploads
        title = request.form.get('title', '')
        sentiment = request.form.get('sentiment')
        description = request.form.get('description', '')
        audio_data = request.form.get('audioData')  # Base64 audio from browser (optional)
        audio_file = request.files.get('audio')     # Uploaded audio file (optional)

        if not files or not files[0]:
            return jsonify({'error': 'No file selected'}), 400

        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400

        audio_filename = None  

        for file in files:
            if file:
                # Validate extension
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                if file_ext not in ALLOWED_EXTENSIONS:
                    return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
                
                file.stream.seek(0) 
                file_header = file.stream.read(2048)
                file.stream.seek(0) 
                mime = magic.Magic(mime=True)
                file_mime_type = mime.from_buffer(file_header)

                if file_mime_type not in ALLOWED_MIME_TYPES:
                    return jsonify({
                        'error': f'File content validation failed. Detected type "{file_mime_type}" is not allowed.'
                    }), 400    

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                # Handle audio upload (either base64 or file)
                if audio_data:
                    audio_filename = f"{secure_filename(title)}.wav"
                    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
                    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                    audio_binary = base64.b64decode(audio_data.split(',')[1])
                    with open(audio_path, "wb") as f:
                        f.write(audio_binary)

                elif audio_file:
                    audio_filename = secure_filename(audio_file.filename)
                    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
                    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                    audio_file.save(audio_path)

                # Always safe to call now
                time_created = datetime.datetime.now()
                save_image(user_id, filename, title, description, time_created, audio_filename, sentiment)
                save_notification(user_id, username, filename, title, time_created, sentiment)

                # Generate PDF thumbnail if applicable
                if filename.lower().endswith('.pdf'):
                    generate_pdf_thumbnail(filepath, filename)

        return jsonify({'message': 'Upload successful'}), 200

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")  # Add logging
        return jsonify({'error': f'Error uploading file: {str(e)}'}), 500


api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=api_key)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        pass

@app.route('/api/analyze-media', methods=['POST'])
def analyze_media():

    image_file = request.files.get('image')
    audio_file = request.files.get('audio')

    prompt_parts = []

    if image_file and image_file.mimetype == 'application/pdf':
        return jsonify({
            "title": "PDF Document Uploaded",
            "description": "Please provide a description for this PDF file.",
            "sentiment": "neutral"
        })

    if not image_file and not audio_file:
        return jsonify({"error": "No media provided for analysis"}), 400

    if image_file:
        image_data = image_file.read()
        image_parts = [{"mime_type": image_file.mimetype, "data": image_data}]
        prompt_parts.extend(image_parts)
        prompt_parts.append("\nAnalyze the image.")
    # for audio file
    if audio_file:
        transcript = "This is a placeholder for the transcribed audio text."
        prompt_parts.append(f"\nAlso consider this audio transcript: '{transcript}'.")

    prompt_parts.append(
        """
        Based on the media provided, generate ONLY a single, valid JSON object with the following keys:
        1. "title": A short, descriptive title (max 10 words).
        2. "description": A concise summary (2-3 sentences).
        3. "sentiment": Classify the overall mood as strictly one of 'positive', 'neutral', or 'negative'.
        Do not include any other text, explanations, or markdown formatting like ```json.
        """
    )

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt_parts)

        # Check if the response was blocked due to safety settings
        if not response.parts:
            error_message = f"Response was blocked. Feedback: {response.prompt_feedback}"
            print(f"⚠️ {error_message}")
            return jsonify({"error": "Content blocked by safety filters"}), 400

        raw_text = response.text


        # Use regex to find the JSON block, even if there's extra text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group())
                # Ensure required keys exist
                if not all(k in parsed for k in ("title", "description", "sentiment")):
                    logging.error(f"AI JSON missing keys: {parsed}")
                    return jsonify({"error": "AI response JSON missing required keys"}), 500
                return jsonify(parsed), 200
            except Exception as e:
                logging.error(f"Error parsing AI JSON: {e}\nRaw response: {raw_text}")
                return jsonify({"error": "Failed to parse AI response JSON"}), 500
        else:
            logging.error(f"No JSON found in AI response: {raw_text}")
            return jsonify({"error": "No JSON object found in AI response"}), 500

    except Exception as e:
        logging.error(f"analyze_media error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error analyzing media: {str(e)}"}), 500

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
        mark_seen = request.args.get('mark_seen', 'false').lower() == 'true'
        # Get all unseen notifications
        notifications = list(notification_collection.find({"seen": False}).sort("timestamp", -1))
        # Mark them as seen if requested
        if mark_seen and notifications:
            notification_ids = [n['_id'] for n in notifications]
            notification_collection.update_many({"_id": {"$in": notification_ids}}, {"$set": {"seen": True}})
        # Convert ObjectId and datetime to string for JSON
        for n in notifications:
            n['_id'] = str(n['_id'])
            if 'timestamp' in n:
                n['timestamp'] = n['timestamp'].isoformat()
        return jsonify({"notifications": notifications}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        timestamp = datetime.datetime.now()
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
