import base64
import json
import os
import datetime
import pathlib
import re
import sys
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session, send_from_directory
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
from routes import home_bp, register_bp, login_pb, logout_pb, google_login, profile_pb
from auth.auth import login_is_required, role_required

from Database.admindatahandler import check_admin_available, create_admin
from Database.userdatahandler import (
    delete_image,
    get_image_by_id, 
    get_images_by_user, 
    get_user_by_username,
    get_user_by_email,  
    save_image, 
    update_image,
    total_images,
    todays_images,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.OAuth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'heif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'beehive'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PDF_THUMBNAIL_FOLDER'] = 'static/uploads/thumbnails/'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

app.register_blueprint(home_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_pb, url_prefix='/')
app.register_blueprint(logout_pb)
app.register_blueprint(google_login)
app.register_blueprint(profile_pb)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/admin/login/callback"
)


@app.route('/login/google')
def login_google():
    # Create a flow instance for user authentication
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://127.0.0.1:5000/login/google/callback"
    )
    
    authorization_url, state = user_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/login/google/callback')
def user_authorize():
    # Create a flow instance for the callback
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://127.0.0.1:5000/login/google/callback"
    )
    
    user_flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = user_flow.credentials
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
    
    # Check if this is an admin email
    if session["email"] in ALLOWED_EMAILS:
        if check_admin_available(session["google_id"]):
            create_admin(session["name"], session["email"], session["google_id"], datetime.datetime.now())
        return redirect("/admin")
    else:
        # Handle regular user login via Google
        user = get_user_by_email(session["email"])
        
        if user:
            # User exists, set session and redirect to profile
            session["username"] = user["username"]
            flash('Login successful via Google!', 'success')
            return redirect(url_for("profile"))
        else:
            # User doesn't exist yet
            session["google_login_pending"] = True
            flash('No account exists with this email. Would you like to create one?', 'info')
            return redirect(url_for("google_register"))


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

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'username' not in session:
        flash('Please log in to update your profile photo.', 'danger')
        return redirect(url_for('login'))
    
    username = session['username']
    user = get_user_by_username(username)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))
    
    if 'profile_photo' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('profile'))
    
    file = request.files['profile_photo']
    
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        filename = f"{username}_profile.{file.filename.rsplit('.', 1)[1].lower()}"
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'profile')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Create missing directories
        
        filepath = os.path.join(upload_folder, filename)
        
        # Remove old profile photo if it exists
        if user.get('profile_photo'):
            old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'profile', user['profile_photo'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save the new file
        file.save(filepath)
        
        # Update user record in database with the new profile photo filename
        userdatahandler.update_profile_photo(username, filename)
        
        flash('Profile photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Only jpg, jpeg, png, and gif files are allowed.', 'danger')
    
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

@app.route('/change-username', methods=['GET', 'POST'])
def change_username():
    username = session['username']
    users_collection = get_user_by_username(username)
    user_id = users_collection.get('_id')
    if request.method == 'POST':
        new_username = request.form.get('new_username')

        # Check if username already exists
        from Database.userdatahandler import is_username_available
        if not is_username_available(new_username):
            flash("Username already taken!", "danger")
            return redirect(url_for('change_username'))

        from Database.userdatahandler import update_username
        update_username(user_id, new_username)
        session['username'] = new_username
        flash("Username updated successfully!", "success")
        

    return render_template('profile.html')

    
@app.route('/change-email', methods=['GET', 'POST'])
def change_email():

    username = session['username']
    users_collection = get_user_by_username(username)
    user_id = users_collection.get('_id')

    if request.method == 'POST':
        new_email = request.form.get('new_email')

        from Database.userdatahandler import update_email
        update_email(user_id, new_email)
        flash("Email updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/change-password', methods=['POST'])
def change_password():

    username = session['username']
    users_collection = get_user_by_username(username)
    user_id = users_collection.get('_id')

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    stored_password = users_collection["password"]
    
    # Verify the current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password):
        flash("Current password is incorrect!", "danger")
        return redirect(url_for('profile'))

    from Database.userdatahandler import update_password
    update_password(user_id, new_password)

    flash("Password updated successfully!", "success")
    return redirect(url_for('profile'))   

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
    google_id = session.get("google_id")
    total_img = total_images()
    todays_image = todays_images()
    
    # Get admin profile photo
    from Database.admindatahandler import get_admin_by_google_id
    admin = get_admin_by_google_id(google_id)
    admin_photo = admin.get('profile_photo') if admin else None
    
    return render_template("admin.html", admin_name=admin_name, total_img=total_img, 
                          todays_image=todays_image, admin_photo=admin_photo)

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

@app.route('/upload_admin_profile_photo', methods=['POST'])
def upload_admin_profile_photo():
    if 'google_id' not in session:
        flash('Please log in to update your profile photo.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Manually check for admin role
    from Database.admindatahandler import is_admin
    if not is_admin():
        return render_template('403.html')
    
    google_id = session["google_id"]
    
    if 'profile_photo' not in request.files:
        flash('No file selected.', 'danger')
        return redirect("/admin")
    
    file = request.files['profile_photo']
    
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect("/admin")
    
    if file and allowed_file(file.filename):
        filename = f"admin_{google_id}_profile.{file.filename.rsplit('.', 1)[1].lower()}"
        profile_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profile')
        
        # Create directory if it doesn't exist
        os.makedirs(profile_dir, exist_ok=True)
        
        filepath = os.path.join(profile_dir, filename)
        
        # Get admin data to check if old profile photo exists
        from Database.admindatahandler import get_admin_by_google_id
        admin = get_admin_by_google_id(google_id)
        
        # Remove old profile photo if it exists
        if admin and admin.get('profile_photo'):
            old_filepath = os.path.join(profile_dir, admin['profile_photo'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save the new file
        file.save(filepath)
        
        # Update admin record in database
        from Database.admindatahandler import update_admin_profile_photo
        update_admin_profile_photo(google_id, filename)
        
        flash('Profile photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Only jpg, jpeg, png, and gif files are allowed.', 'danger')
    
    return redirect("/admin")

if __name__ == '__main__':
    app.run(debug=True)
