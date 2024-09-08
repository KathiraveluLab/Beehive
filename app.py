import json
import os
import datetime
import pathlib
from tkinter import ALL
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol


from Database.userdatahandler import (
    create_user, 
    delete_image, 
    get_image_by_id, 
    get_images_by_user, 
    get_password_by_username, 
    get_user_by_username, 
    is_email_available, 
    is_username_available, 
    save_image, 
    update_image
)


from OAuth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID
import users.valid_username as valid_username


app = Flask(__name__)
app.secret_key = 'beehive'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
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
        if stored_password == password:
            session['username'] = username  # Store the username in session
            flash('Login successful!', 'success')
            return redirect(url_for("profile"))
        else:
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
            if is_email_available(email):
                if is_username_available(username):
                    account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                    create_user(first_name, last_name, email, username, password, account_created_at)
                    flash('Registration successful!', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('This Username already taken.', 'danger')
            else:
                flash('This Email already signed in.', 'danger')

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

    return render_template("profile.html", username=user['username'], full_name=f"{user['first_name']} {user['last_name']}", images=images)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'username' not in session:
        flash('Please log in to upload images.', 'danger')
        return redirect(url_for('login'))

    user = get_user_by_username(session['username'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    file = request.files['file']
    title = request.form['title']
    description = request.form['description']

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        save_image(user['username'], filename, title, description)
        flash('Image uploaded successfully!', 'success')
    else:
        flash('No file selected.', 'danger')

    return redirect(url_for('profile'))

# Edit images uploaded by the user
@app.route('/edit/<image_id>', methods=['POST'])
def edit_image(image_id):
    if 'username' not in session:
        flash('Please log in to edit images.', 'danger')
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']

    try:
        image_id = ObjectId(image_id)
    except Exception as e:
        flash(f'Invalid image ID format: {str(e)}', 'danger')
        return redirect(url_for('profile'))

    update_image(image_id, title, description)
    flash('Image updated successfully!', 'success')
    return redirect(url_for('profile'))

# Delete images uploaded by the user
@app.route('/delete/<image_id>')
def delete_image_route(image_id):
    if 'username' not in session:
        flash('Please log in to delete images.', 'danger')
        return redirect(url_for('login'))

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

    return redirect(url_for('profile'))


# Logout the user
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

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
    if session["email"] in ALLOWED_EMAILS:
        with open('user_info.json', 'w') as json_file:
            json.dump(session, json_file, indent=4)
        return redirect("/admin")
    else:
        flash("You are not authorized to access the admin dashboard.", "danger")
        return redirect("/")



@app.route("/admin")
@login_is_required
def protected_area():
    return f'Hello {session["name"]}, welcome to the Admin Dashboard!'

@app.route("/admin/logout")
def adminlogout():
    session.clear()
    return redirect("/")


# Additional routes for other admin functionalities
@app.route('/admin/profile')
def admin_profile():
    user = session.get('user')
    if not user:
        flash("You must log in as an admin to view your profile.")
        return redirect(url_for('login'))
    return f'Admin Profile: {user["name"]}'

@app.route('/admin/settings')
def admin_settings():
    user = session.get('user')
    if not user:
        flash("You must log in as an admin to access settings.")
        return redirect(url_for('login'))
    return 'Admin Settings Page'


if __name__ == '__main__':
    app.run(debug=True)
