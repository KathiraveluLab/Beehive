import base64
from functools import wraps
import json
import os
import datetime
import pathlib
import re
import sys
from tkinter import ALL
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from bson import ObjectId
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol
from Database import userdatahandler
from werkzeug.utils import secure_filename
import fitz  
from PIL import Image
import bcrypt


from Database.admindatahandler import check_admin_available, create_admin, is_admin
from Database.userdatahandler import (
    create_user, 
    delete_image,
    get_currentuser_from_session, 
    get_image_by_id, 
    get_images_by_user, 
    get_password_by_username, 
    get_user_by_username, 
    is_email_available, 
    is_username_available,
    isValidEmail, 
    save_image, 
    update_image,
    total_images,
    todays_images,
)
from usersutils import valid_username

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from OAuth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'heif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'beehive'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_THUMBNAIL_FOLDER'] = 'static/uploads/thumbnails/'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/admin/login/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  
        else:
            return function()

    return wrapper

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if "google_id" in session:
                if required_role == 'admin' and not is_admin():
                    return render_template('403.html')
                
            elif "username" in session:
                user = get_currentuser_from_session()
                
                if user is None:
                    print("User not found in session!")
                    return render_template('403.html')  

                if user.get('role') != required_role:
                    return render_template('403.html')

            else:
                return render_template('403.html')

            return func(*args, **kwargs)

        return wrapper
    return decorator

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Login the user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        stored_password = get_password_by_username(username)
        
        if stored_password:
            # Check if stored password is hashed
            if isinstance(stored_password, bytes) and stored_password.startswith(b'$2b$'):
                # Handle hashed password
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password)
            else:
                # For plain text password
                is_valid = (stored_password == password)
            
            if is_valid:
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for("profile"))
                
        flash('Invalid credentials, please try again.', 'danger')
    return render_template("login.html")

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_created_at = None

        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        elif password != confirm_password:
            flash('Passwords do not match, please try again.', 'danger')
        else:
                if isValidEmail(email) and is_email_available(email) and is_username_available(username):
                    if is_username_available(username):
                        account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                        create_user(first_name, last_name, email, username, password, account_created_at)
                        flash('Registration successful!', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('This Username already taken.', 'danger')
                else:
                    flash('This Email is already in use!', 'danger')


    return render_template("register.html")

# Display the user's profile page
@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Please log in to access the profile page.', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    user = get_user_by_username(username)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    images = get_images_by_user(username)  # Fetch images uploaded by the user

    return render_template(
        "profile.html", 
        username=user['username'], 
        full_name=f"{user['first_name']} {user['last_name']}", 
        images=images
    )

@app.route('/upload', methods=['POST'])
def upload_images():
    if 'username' not in session:
        flash('Please log in to upload images.', 'danger')
        return redirect(url_for('login'))

    user = get_user_by_username(session['username'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    files = request.files.getlist('files')  # Supports multiple file uploads
    title = request.form.get('title', '')
    sentiment = request.form.get('sentiment')
    description = request.form.get('description', '')
    audio_data = request.form.get('audioData')

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

            # Handle audio file if provided
            audio_filename = None
            if audio_data:
                audio_filename = f"{secure_filename(title)}.wav"
                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                audio_binary = base64.b64decode(audio_data.split(',')[1])
                with open(audio_path, "wb") as f:
                    f.write(audio_binary)

        time_created = datetime.datetime.now()
        save_image(user['username'], filename, title, description, time_created, audio_filename, sentiment)
        flash('Image uploaded successfully!', 'success')

            # Generate PDF thumbnail if applicable
        if filename.lower().endswith('.pdf'):
                generate_pdf_thumbnail(filepath, filename)

        else:
            flash('Invalid file type or no file selected.', 'danger')

    return redirect(url_for('profile'))

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
@app.route('/edit/<image_id>', methods=['POST'])
def edit_image(image_id):
    
    if 'username' in session or 'google_id' in session:
        title = request.form['title']
        description = request.form['description']

        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            flash(f'Invalid image ID format: {str(e)}', 'danger')
            return redirect(url_for('profile'))

        update_image(image_id, title, description)
        flash('Image updated successfully!', 'success')
        if 'username' in session:
            return redirect(url_for('profile'))
        elif 'google_id' in session:
            return redirect(url_for('getallusers'))
        return redirect(url_for('login'))
    else:
        flash('Please log in to edit images.', 'danger')
        return redirect(url_for('login'))
 
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
   
# Delete images uploaded by the user
@app.route('/delete/<image_id>')
def delete_image_route(image_id):

    if 'username' in session or 'google_id' in session:
        
        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            flash(f'Invalid image ID format: {str(e)}', 'danger')
            return redirect(url_for('profile'))

        image = get_image_by_id(image_id)
        if not image:
            flash('Image not found.', 'danger')
            return redirect(url_for('profile'))
        # Delete image file from upload directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
            flash(f'Image file deleted: {image["filename"]}', 'success')
        else:
            flash('Image file not found in upload directory.', 'danger')

        # Delete image record from database
        delete_image(image_id)
        flash('Image record deleted from database.', 'success')
        if 'username' in session:
            return redirect(url_for('profile'))
        elif 'google_id' in session:
            return redirect(url_for('getallusers'))
        return redirect(url_for('login'))
    else:
        flash('Please log in to delete images.', 'danger')
        return redirect(url_for('login'))

    


# Logout the user
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# Admin routes

@app.route("/signingoogle")
def signingoogle():
    return render_template("signingoogle.html")

@app.route('/admin/login')
def admin_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/admin/login/callback')
def authorize():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    if session["email"] in ALLOWED_EMAILS :
        if check_admin_available(session["google_id"]):
            create_admin(session["name"], session["email"], session["google_id"], datetime.datetime.now())
        with open('user_info.json', 'w') as json_file:
            json.dump(session, json_file, indent=4)
        return redirect("/admin")
    else:
        return render_template("403.html")



@app.route("/admin")
@role_required("admin")
@login_is_required
def protected_area():
    admin_name = session.get("name")
    total_img = total_images()
    todays_image = todays_images()
    return render_template("admin.html", admin_name=admin_name, total_img=total_img, todays_image = todays_image)

@login_is_required
@role_required("admin")
@app.route("/admin/logout")
def adminlogout():
    session.clear()
    return redirect("/")



@app.route('/admin/users')
@role_required("admin")
def getallusers():
    users = userdatahandler.getallusers()
    return render_template('users.html', users=users)



@app.route('/admin/users/<username>')
@role_required("admin")
def user_images_show(username):
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('getallusers'))
    
    images = get_images_by_user(username)
    return render_template(
        'user_images.html',
        username=username,
        images=images,
        full_name=f"{user['first_name']} {user['last_name']}"
    )



if __name__ == '__main__':
    app.run(debug=True)
