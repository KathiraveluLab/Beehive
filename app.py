import json
import os
import datetime
import pathlib
import re
import sys
from tkinter import ALL
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol
from Database import userdatahandler


from Database.admindatahandler import check_admin_available, create_admin
from Database.userdatahandler import (
    create_user, 
    delete_image, 
    get_image_by_id, 
    get_images_by_user, 
    get_password_by_username, 
    get_user_by_username, 
    is_email_available, 
    is_username_available,
    isValidEmail, 
    save_image, 
    update_image
)
from usersutils import valid_username

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from OAuth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID
from datetime import datetime



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
        category = request.form['category']
        account_created_at = None

        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        elif password != confirm_password:
            flash('Passwords do not match, please try again.', 'danger')
        else:
                if isValidEmail(email) and is_email_available(email) and is_username_available(username):
                    if is_username_available(username):
                        account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                        create_user(first_name, last_name, email, username, password,category, account_created_at)
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
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        save_image(user['username'], filename, title, description)
        flash('Image uploaded successfully!', 'success')
    else:
        flash('No file selected.', 'danger')

    return redirect(url_for('profile'))

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
        return render_template("404.html")

def getallimages():
     images_collection = list(beehive_image_collection.find())
     users_collection = list(beehive_user_collection.find())
     return images_collection, users_collection

@app.route("/admin", methods=["GET", "POST"])
# @login_is_required
def protected_area():
    admin_name = session.get("name")
    images, users_collection = userdatahandler.getallimages()
    
    image_counts_by_day = {}
    image_counts_by_category = {}
    
    # Default values
    filter_date = None
    filter_category = None

    # Checking if filter parameters are provided in the request
    if request.method == "POST":
        filter_date = request.form.get("filter_date")
        filter_category = request.form.get("filter_category")
        
        if filter_date:
            images = [img for img in images if img['_id'].generation_time.date() == datetime.strptime(filter_date, '%Y-%m-%d').date()]
        if filter_category:
            users_with_category = {user['username']: user for user in users_collection}
            images = [img for img in images if users_with_category[img['username']]['category'] == filter_category]
    
    # Calculate image stats
    for image in images:
        username = image['username']  # Assuming the image has the 'username' field
        user_details = next((user for user in users_collection if user['username'] == username), None)

        if user_details:
            category = user_details['category']  # Get category from user details
        else:
            category = 'Unknown'  # Handle case where username doesn't match

        # Extracting the date from the `_id`
        date = image['_id'].generation_time.date()
        
        # Counting images per day
        if date not in image_counts_by_day:
            image_counts_by_day[date] = 0
        image_counts_by_day[date] += 1
        
        # Counting images per category
        if category not in image_counts_by_category:
            image_counts_by_category[category] = 0
        image_counts_by_category[category] += 1

    # Calculate total users
    total_users = len(users_collection)
    
    # Calculate users by category
    users_by_category = {}
    for user in users_collection:
        category = user['category']
        if category not in users_by_category:
            users_by_category[category] = 0
        users_by_category[category] += 1

    return render_template(
        "admin.html", 
        admin_name=admin_name, 
        image_counts_by_day=image_counts_by_day, 
        image_counts_by_category=image_counts_by_category,
        total_users=total_users,
        users_by_category=users_by_category,
        filter_date=filter_date,
        filter_category=filter_category
    )


@app.route("/admin/logout")
def adminlogout():
    session.clear()
    return redirect("/")


@app.route('/admin/users')
def getallusers():
    users = userdatahandler.getallusers()
    # print(users)
    return render_template('users.html', users=users)

@app.route('/admin/users/<username>')
def user_images_show(username):
    images = get_images_by_user(username)
    return render_template('user_images.html', images=images, username=username)



if __name__ == '__main__':
    app.run(debug=True)
