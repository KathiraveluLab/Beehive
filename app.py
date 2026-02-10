from dotenv import load_dotenv
load_dotenv()
import os

# Validate configuration early - fail fast if config is missing or insecure
# Skip validation in test mode to avoid breaking tests
if not os.getenv('TESTING'):
    from config import Config
    Config.validate_config()

import base64
import binascii
import datetime
import json
import logging
import os
import pathlib
import re
import sys
import traceback
from datetime import timedelta
from functools import wraps
from utils.sanitize import sanitize_text
from utils.logger import logger as app_logger

import bcrypt
import fitz
import google.auth.transport.requests
import google.generativeai as genai
import magic
import requests
from bson import ObjectId
from bson.errors import InvalidId
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_cors import CORS
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from PIL import Image
from pip._vendor import cachecontrol
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

from database import userdatahandler
from database.admindatahandler import is_admin
from database.databaseConfig import (
    get_beehive_message_collection,
    get_beehive_notification_collection,
)
from database.databaseConfig import get_beehive_user_collection
from database.userdatahandler import (
    delete_image,
    get_all_users,
    get_image_by_id,
    get_image_by_audio_filename,
    get_images_by_user,
    _get_paginated_images_by_user,
    get_user_by_username,
    save_image,
    save_notification,
    update_image,
)
from utils.pagination import parse_pagination_params

from utils.jwt_auth import require_auth,require_admin_role 
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        },
        r"/delete/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        },
        r"/edit/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        },
        r"/audio/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)
from config import Config

app.config.from_object(Config)

app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT") or 587),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
)

mail = Mail(app)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from oauth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "heif", "pdf", "avif"}

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/heif",
    "application/pdf",
    "image/avif",
}

ALLOWED_AUDIO_MIME_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "audio/opus",
    "video/webm",  # Some browsers label audio-only webm as video/webm
    "video/ogg",   # Defensive allow for ogg containers
    "application/ogg",  # libmagic may report this for ogg
}
MAX_AUDIO_FILE_SIZE = 6 * 1024 * 1024  # We can set the size required to Beehive 
AUDIO_DATA_URL_RE = re.compile(r"^data:(?P<mime>[-\w.+/]+);base64,(?P<data>[A-Za-z0-9+/=\r\n]+)$")

# Initialized global MIME detector
try:
    MAGIC = magic.Magic(mime=True)
except Exception as e:
    MAGIC = None
    app_logger.error(
        "MIME detection unavailable: failed to initialize libmagic. Install system libmagic (e.g., `apt-get install libmagic1` or equivalent) and python-magic. Error: %s",
        e,
    )

# Fallback detector initialized lazily if the global MAGIC is unavailable
_FALLBACK_MAGIC = None

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if (
    not app.secret_key
    or len(app.secret_key) < 32
    or app.secret_key in {"beehive", "beehive-secret-key"}
):
    raise ValueError(
        "CRITICAL: Set a secure FLASK_SECRET_KEY (at least 32 characters) in the environment!"
    )
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["PDF_THUMBNAIL_FOLDER"] = "static/uploads/thumbnails/"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://127.0.0.1:5000/admin/login/callback",
)


MIME_SIZE_LIMITS = {
    "image/jpeg": 10*1024*1024 ,
    "image/png": 10 *1024*1024,
    "image/webp": 10 * 1024 * 1024,
    "image/gif": 8 * 1024 * 1024,
    "image/heif": 15 * 1024 * 1024,
    "image/heic": 15 * 1024 * 1024,
    "application/pdf": 25 * 1024 * 1024,
}

def validate_file_size(file, mime_type, filename):
    """
    Validates the file size against allowed limits.
    Returns None if valid, otherwise a response tuple.
    """
    # Determine max allowed size
    max_allowed = MIME_SIZE_LIMITS.get(mime_type)

    if max_allowed is None:
        return jsonify({"error": f"Unsupported MIME type: {mime_type}"}), 400

    # Detect actual file size
    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > max_allowed:
        return (
            jsonify({
                "error": f"File '{filename}' exceeds max size limit "
                         f"({max_allowed // (1024 * 1024)}MB)"
            }),
            413,
        )
    return None


def _build_audio_basename(title: str) -> str:
    safe_title = secure_filename(title) or "audio"
    # Keep filenames short and predictable
    return safe_title[:80]


def _audio_size_error():
    return (
        jsonify(
            {
                "error": f"Audio exceeds max size limit ({MAX_AUDIO_FILE_SIZE // (1024 * 1024)}MB)",
            }
        ),
        413,
    )


def _validate_audio_size(size_bytes):
    if size_bytes > MAX_AUDIO_FILE_SIZE:
        return _audio_size_error()
    return None


def _decode_audio_data(audio_data):
    """
    Validates and decodes a base64 audio data URL.
    Returns (bytes, None) when valid or (None, response) when invalid.
    """
    match = AUDIO_DATA_URL_RE.match(audio_data.strip()) if audio_data else None
    if not match:
        return None, (jsonify({"error": "Invalid audio data URL format"}), 400)

    mime_type = match.group("mime").lower()
    base_mime = mime_type.split(";")[0].strip()
    if base_mime not in ALLOWED_AUDIO_MIME_TYPES:
        return None, (jsonify({"error": "Unsupported audio MIME type"}), 400)

    b64_payload = match.group("data").strip()
    estimated_size = (len(b64_payload) * 3) // 4
    size_error = _validate_audio_size(estimated_size)
    if size_error:
        return None, size_error

    try:
        audio_binary = base64.b64decode(b64_payload, validate=True)
    except (binascii.Error, ValueError):
        return None, (jsonify({"error": "Audio data is not valid base64"}), 400)

    size_error = _validate_audio_size(len(audio_binary))
    if size_error:
        return None, size_error

    if base_mime.startswith("audio/wav") and not (
        audio_binary.startswith(b"RIFF") and audio_binary[8:12] == b"WAVE"
    ):
        return None, (jsonify({"error": "Audio content validation failed"}), 400)

    return audio_binary, base_mime


def _validate_audio_file_upload(audio_file):
    if not audio_file or not audio_file.filename:
        return jsonify({"error": "No audio file provided"}), 400

    filename = secure_filename(audio_file.filename)
    if not filename:
        return jsonify({"error": "Invalid audio filename"}), 400

    header = audio_file.stream.read(2048)
    audio_file.stream.seek(0)
    detected_mime = (MAGIC.from_buffer(header) if MAGIC else None) or (
        audio_file.mimetype.lower() if audio_file.mimetype else ""
    )
    base_mime = detected_mime.split(";")[0].strip() if detected_mime else ""

    if base_mime not in ALLOWED_AUDIO_MIME_TYPES:
        return jsonify({"error": "Audio file type not allowed"}), 400

    audio_file.stream.seek(0, os.SEEK_END)
    size = audio_file.stream.tell()
    audio_file.stream.seek(0)
    size_error = _validate_audio_size(size)
    if size_error:
        return size_error

    return None

AUDIO_MIME_TO_EXTENSION = {
    "audio/webm": ".webm",
    "video/webm": ".webm",
    "audio/ogg": ".ogg",
    "video/ogg": ".ogg",
    "application/ogg": ".ogg",
    "audio/opus": ".opus",
    "audio/x-wav": ".wav",
    "audio/wav": ".wav",
}

# Upload images
@app.route("/api/user/upload", methods=["POST"])
@require_auth
def upload_images():
    user_id = request.current_user["id"]
    try:
        username = sanitize_text(request.form.get("username", ""))
        files = request.files.getlist("files")  # Supports multiple file uploads
        title = sanitize_text(request.form.get("title", ""))
        sentiment = sanitize_text(request.form.get("sentiment"))
        description = sanitize_text(request.form.get("description", ""))
        audio_data = request.form.get(
            "audioData"
        )  # Base64 audio from browser (optional)
        audio_file = request.files.get("audio")  # Uploaded audio file (optional)

        if not files or not files[0]:
            return jsonify({"error": "No file selected"}), 400

        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400

        audio_filename = None
        safe_audio_basename = _build_audio_basename(title)

        # Prefer the global MIME detector to avoid per-file instantiation; fall back lazily if unavailable
        if MAGIC is not None:
            mime_detector = MAGIC
        else:
            global _FALLBACK_MAGIC
            if _FALLBACK_MAGIC is None:
                try:
                    _FALLBACK_MAGIC = magic.Magic(mime=True)
                except Exception as e:
                    app_logger.error(
                        "MIME detection unavailable: libmagic missing or misconfigured. Install system libmagic and python-magic. Error: %s",
                        e,
                    )
                    return jsonify({"error": "Server MIME detection unavailable; contact administrator."}), 500
            mime_detector = _FALLBACK_MAGIC

        for file in files:
            if file:
                # Validate extension
                original_filename = secure_filename(file.filename)
                unique_filename = f"{ObjectId()}_{original_filename}"
                file_ext = os.path.splitext(original_filename)[1].lstrip('.').lower()
                if file_ext not in ALLOWED_EXTENSIONS:
                    return jsonify(
                        {
                            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                        }
                    ), 400

                file.stream.seek(0)
                file_header = file.stream.read(2048)
                file.stream.seek(0)
                file_mime_type = mime_detector.from_buffer(file_header)

                if file_mime_type not in ALLOWED_MIME_TYPES:
                    return jsonify(
                        {
                            "error": f'File content validation failed. Detected type "{file_mime_type}" is not allowed.'
                        }
                    ), 400
                    
                size_error = validate_file_size(file, file_mime_type, original_filename)
                if size_error:
                    return size_error

                filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                # Handle audio upload (either base64 or file)
                if audio_data:
                    audio_binary, audio_mime_or_error = _decode_audio_data(audio_data)
                    if not isinstance(audio_binary, (bytes, bytearray)):
                        # audio_mime_or_error holds the response tuple in this case
                        return audio_mime_or_error

                    audio_mime = audio_mime_or_error  # safe: decode returns mime on success
                    audio_ext = audio_ext = AUDIO_MIME_TO_EXTENSION.get(audio_mime, ".wav")

                    audio_filename = f"{safe_audio_basename}_{ObjectId()}{audio_ext}"
                    audio_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], audio_filename
                    )
                    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                    with open(audio_path, "wb") as f:
                        f.write(audio_binary)

                elif audio_file:
                    audio_error = _validate_audio_file_upload(audio_file)
                    if audio_error:
                        return audio_error

                    audio_ext = pathlib.Path(audio_file.filename).suffix.lower() or ".wav"
                    audio_filename = f"{safe_audio_basename}_{ObjectId()}{audio_ext}"
                    audio_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], audio_filename
                    )
                    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                    audio_file.save(audio_path)

                # Always safe to call now
                time_created = datetime.datetime.now()
                save_image(
                    user_id,
                    unique_filename,
                    title,
                    description,
                    time_created,
                    audio_filename,
                    sentiment,
                )
                save_notification(
                    user_id, username, unique_filename, title, time_created, sentiment
                )

                # Generate PDF thumbnail if applicable
                if unique_filename.lower().endswith(".pdf"):
                    generate_pdf_thumbnail(filepath, unique_filename)

        return jsonify({"message": "Upload successful"}), 200

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")  # Add logging
        return jsonify({"error": "Failed to upload file. Please try again."}), 500


api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_google_api_key_here":
    app_logger.warning(
        "GOOGLE_API_KEY not properly configured. AI features will be disabled."
    )
    genai_configured = False
else:
    try:
        genai.configure(api_key=api_key)
        # Test the API key by listing models
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                pass
        genai_configured = True
        app_logger.info("Google Generative AI configured successfully")
    except Exception as e:
        app_logger.warning(f"Failed to configure Google Generative AI: {e}")
        app_logger.warning("AI features will be disabled.")
        genai_configured = False


@app.route("/api/analyze-media", methods=["POST"])
@require_auth
def analyze_media():
    user_id = request.current_user["id"]
    image_file = request.files.get("image")
    audio_file = request.files.get("audio")

    if not genai_configured:
        return jsonify({"error": "AI analysis not configured on server. Set a valid GOOGLE_API_KEY."}), 503

    prompt_parts = []

    if image_file and image_file.mimetype == "application/pdf":
        return jsonify(
            {
                "title": "PDF Document Uploaded",
                "description": "Please provide a description for this PDF file.",
                "sentiment": "neutral",
            }
        )

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
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt_parts)

        # Check if the response was blocked due to safety settings
        if not response.parts:
            error_message = (
                f"Response was blocked. Feedback: {response.prompt_feedback}"
            )
            app_logger.warning(f"AI Response blocked: {error_message}")
            return jsonify({"error": "Content blocked by safety filters"}), 400

        raw_text = response.text

        # Use regex to find the JSON block, even if there's extra text
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group())
                # Ensure required keys exist
                if not all(k in parsed for k in ("title", "description", "sentiment")):
                    logging.error(f"User {user_id}: AI JSON missing keys: {parsed}")
                    return jsonify(
                        {"error": "AI response JSON missing required keys"}
                    ), 500
                return jsonify(parsed), 200
            except Exception as e:
                logging.error(f"User {user_id}: Error parsing AI JSON: {e}\nRaw response: {raw_text}")
                return jsonify({"error": "Failed to parse AI response JSON"}), 500
        else:
            logging.error(f"User {user_id}: No JSON found in AI response: {raw_text}")
            return jsonify({"error": "No JSON object found in AI response"}), 500

    except Exception as e:
        logging.error(f"User {user_id}: analyze_media error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to analyze media. Please try again."}), 500


# generate thumbnail for the pdf
def generate_pdf_thumbnail(pdf_path, filename):
    """Generate an image from the first page of a PDF using PyMuPDF."""
    # Ensure the thumbnails directory exists
    thumbnails_dir = os.path.join(app.config["UPLOAD_FOLDER"], "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)

    pdf_document = fitz.open(pdf_path)

    # select only the first page for the thumbnail
    first_page = pdf_document.load_page(0)

    zoom = 2  # Increase for higher resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = first_page.get_pixmap(matrix=mat)

    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Robust filename handling
    name, _ = os.path.splitext(filename)
    thumbnail_filename = f"{name}.jpg"
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    image.save(thumbnail_path, "JPEG")

    return thumbnail_path



def check_owner(current_id, resource_id):
    """Compares two IDs for equality by converting them to strings to handle type differences."""
    return str(current_id) == str(resource_id)

# Edit images uploaded by the user
@app.route("/edit/<image_id>", methods=["PATCH"])
@require_auth
def edit_image(image_id):
    try:
        # Get form data
        title = sanitize_text(request.form.get("title"))
        description = sanitize_text(request.form.get("description"))
        sentiment = sanitize_text(request.form.get("sentiment", ""))

        if not title or not description:
            return jsonify({"error": "Title and description are required."}), 400

        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            logging.error(f"Invalid Image ID fromat for image_id '{image_id}':{e}")
            return jsonify({"error": "Invalid image ID format."}), 400

        # Verify the image exists
        image = get_image_by_id(image_id)
        if not image:
            return jsonify({"error": "Image not found."}), 404
        # verify the ownership
        current_user_id = request.current_user["id"]
        image_owner_id = image["user_id"]

        if not check_owner(current_user_id, image_owner_id):
            return jsonify({"error": "Unauthorized: You do not own this image."}), 403

        # Update the image
        update_image(image_id, title, description, sentiment)
        return jsonify({"message": "Image updated successfully!"}), 200

    except Exception as e:
        logging.error(f"Error updating image: {str(e)}")
        return jsonify({"error": "Failed to update image. Please try again."}), 500


@app.route("/api/audio/<filename>")
@require_auth
def serve_audio(filename):
    """Serve audio files with ownership verification to prevent IDOR attacks."""
    try:
        # Query database to find the image record associated with this audio file
        image = get_image_by_audio_filename(filename)
        
        # If no record found, the audio file doesn't exist or isn't associated with any upload
        if not image:
            return jsonify({"error": "Audio file not found"}), 404
        
        # Get current user info from the JWT token (set by @require_auth decorator)
        current_user_id = request.current_user.get("id")
        current_user_role = request.current_user.get("role", "user")
        image_owner_id = image.get("user_id")
        
        # Allow access if user is admin OR owns the audio file
        is_admin = current_user_role == "admin"
        is_owner = check_owner(current_user_id, image_owner_id)
        
        if not (is_admin or is_owner):
            return jsonify({"error": "Unauthorized: You do not have permission to access this audio file"}), 403
        
        # User is authorized (either admin or owner), serve the file
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
        
    except Exception as e:
        logging.error(f"Error serving audio file '{filename}': {str(e)}")
        return jsonify({"error": "Failed to serve audio file"}), 500


# Delete images uploaded by the user
@app.route("/delete/<image_id>", methods=["DELETE"])
@require_auth
def delete_image_route(image_id):
    try:
        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            logging.error(f"Invalid Image ID fromat for image_id '{image_id}':{e}")            
            logging.error(f"Invalid image ID format for image_id '{image_id}': {e}")
            return jsonify({"error": "Invalid image ID format."}), 400

        # Verify the image exists
        image = get_image_by_id(image_id)
        if not image:
            return jsonify({"error": "Image not found."}), 404
        # verify the ownership of user
        current_user_id = request.current_user.get("id")
        image_owner_id = image.get("user_id")

        if not check_owner(current_user_id, image_owner_id):
            return jsonify({"error": "Unauthorized: You do not own this image."}), 403

        # Delete image file from upload directory
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], image["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
            # Also delete thumbnail if it exists
            if image["filename"].lower().endswith(".pdf"):
                thumbnail_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    "thumbnails",
                    image["filename"].replace(".pdf", ".jpg"),
                )
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

        # Delete audio file if it exists
        if image.get("audio_filename"):
            audio_path = os.path.join(
                app.config["UPLOAD_FOLDER"], image["audio_filename"]
            )
            if os.path.exists(audio_path):
                os.remove(audio_path)

        # Delete image record from database
        delete_image(image_id)
        return jsonify({"message": "Image deleted successfully!"}), 200

    except Exception as e:
        logging.error(f"Error deleting image: {str(e)}")
        return jsonify({"error": "Failed to delete image. Please try again."}), 500


# Get all images uploaded by a user
@app.route("/api/user/user_uploads")
@require_auth
def user_images_show():
    try:
        user_id = request.current_user["id"]
        page, page_size = parse_pagination_params(default_page=1, default_size=12, max_size=50)
        
        # Extract filter parameters from query string
        filters = {
            'q': request.args.get('q'),
            'sentiment': request.args.get('sentiment'),
            'date_filter': request.args.get('date_filter'),
            'from': request.args.get('from'),
            'to': request.args.get('to')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = _get_paginated_images_by_user(user_id, page, page_size, filters if filters else None)
        
        response_data = {
            "images": result['images'],
            "user_id": user_id,
            "total_count": result['total_count'],
            "page": result['page'],
            "pageSize": result['pageSize'],
            "totalPages": result['totalPages'],
            "message": "Success",
        }
        return jsonify(response_data)
    except ValueError as e:
        logging.error(f"Invalid pagination parameters: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error fetching user uploads: {str(e)}")
        return jsonify({"error": "Failed to fetch uploads. Please try again."}), 500


@app.route("/api/admin/notifications", methods=["GET"])
@require_admin_role
def get_admin_notifications():
    try:
        notification_collection = get_beehive_notification_collection()

        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("limit", 5))
        except ValueError:
            return jsonify(
                {"error": "Invalid 'page' or 'limit' parameter. Must be an integer."}
            ), 400
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

        return jsonify(
            {"notifications": notifications, "unseen_count": unseen_count, "page": page}
        ), 200

    except Exception as e:
        logging.error(f"Error fetching admin notifications: {str(e)}")
        return jsonify({"error": "Failed to fetch notifications. Please try again."}), 500


@app.route("/api/admin/notifications/mark_seen", methods=["POST"])
@require_admin_role
def mark_selected_notifications_seen():
    try:
        notification_collection = get_beehive_notification_collection()
        data = request.get_json()

        ids = data.get("ids", [])
        if not ids:
            return jsonify({"status": "no_ids"}), 200
        try:
            object_ids = [ObjectId(_id) for _id in ids]
        except InvalidId:
            return jsonify({"error": "Invalid ID format"}), 400

        # Mark only these notifications seen
        notification_collection.update_many(
            {"_id": {"$in": object_ids}}, {"$set": {"seen": True}}
        )

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logging.error(f"Error marking notifications as seen: {str(e)}")
        return jsonify({"error": "Failed to update notifications. Please try again."}), 500


@app.route("/api/chat/send", methods=["POST"])
@require_auth
def send_chat_message():
    try:
        data = request.json
        from_id = request.current_user["id"]
        from_role = request.current_user["role"]
        to_id = data.get("to_id")
        to_role = data.get("to_role")
        content = sanitize_text(data.get("content"))
        timestamp = datetime.datetime.now()
        if not (from_id and from_role and to_id and to_role and content):
            return jsonify({"error": "Missing required fields"}), 400
        message = {
            "from_id": from_id,
            "from_role": from_role,
            "to_id": to_id,
            "to_role": to_role,
            "content": content,
            "timestamp": timestamp,
        }
        messages_col = get_beehive_message_collection()
        messages_col.insert_one(message)
        return jsonify({"message": "Message sent"}), 200
    except Exception as e:
        logging.error(f"Error sending chat message: {str(e)}")
        return jsonify({"error": "Failed to send message. Please try again."}), 500


@app.route("/api/chat/messages", methods=["GET"])
@require_auth
def get_chat_messages():
    try:
        current_user = request.current_user

        if current_user.get("role") == "admin":
            # If the requester is an admin, they can specify a user_id
            user_id = request.args.get("user_id")
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400
        else:
            # We'll be ignoring any user_id passed in the query to prevent data leakage.
            user_id = current_user["id"]

        messages_col = get_beehive_message_collection()
        # Get messages between this user and admin
        query = {
            "$or": [
                {"from_id": user_id, "to_role": "admin"},
                {"to_id": user_id, "from_role": "admin"},
            ]
        }
        messages = list(messages_col.find(query).sort("timestamp", 1))
        for m in messages:
            m["_id"] = str(m["_id"])
            if "timestamp" in m:
                m["timestamp"] = m["timestamp"].isoformat()
        return jsonify({"messages": messages}), 200
    except Exception as e:
        logging.error(f"Error fetching chat messages: {str(e)}")
        return jsonify({"error": "Failed to fetch messages. Please try again."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and API Gateway.
    Returns 200 if healthy, 503 if issues detected.
    """
    # Fix: Capture timestamp once to ensure consistency (DRY)
    current_time = datetime.datetime.now().isoformat()

    try:
        # Basic app health
        health_status = {"status": "healthy", "timestamp": current_time}
        
        # Optional: Check MongoDB connection
        db_collection = get_beehive_user_collection()
        # Simple ping - will raise exception if DB unreachable
        db_collection.database.command('ping')
        health_status["database"] = "connected"
        
        return jsonify(health_status), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": "Service Unavailable",
            "timestamp": current_time  # Uses the same variable
        }), 503
    

# Import blueprints
from routes.adminroutes import admin_bp

app.register_blueprint(admin_bp)
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix="/api/auth")

if __name__ == "__main__":
    app.run(debug=True)
