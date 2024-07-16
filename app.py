import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session,config
from bson import ObjectId
from Database.DatabaseConfig import (
    create_user, get_image_by_id, get_password_by_username, is_email_available, is_username_available, 
    get_user_by_username, save_image, get_images_by_user, 
    update_image, delete_image
)
import Users.valid_username as valid_username

app = Flask(__name__)
app.secret_key = 'beehive'
app.config['UPLOAD_FOLDER'] = 'static/uploads'



# Home page
@app.route('/')
def home():
    return render_template('login.html')

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


# Upload images to the user's profile
@app.route('/upload', methods=['POST'])
def upload_image():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
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
    update_image(ObjectId(image_id), title, description)
    flash('Image updated successfully!', 'success')
    return redirect(url_for('profile'))

# Delete images uploaded by the user
@app.route('/delete/<image_id>')
def delete_image_route(image_id):
    if 'username' not in session:
        flash('Please log in to delete images.', 'danger')
        return redirect(url_for('login'))


    image = get_image_by_id(ObjectId(image_id))
    if not image:
        flash('Image not found.', 'danger')
        return redirect(url_for('profile'))
    # Delete image file from upload directory
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
            flash(f'Image file deleted: {image["filename"]}', 'success')
        else:
            flash('Image file not found in upload directory.', 'danger')
    except Exception as e:
        flash(f'Failed to delete image file: {str(e)}', 'danger')
    # Delete image record from database
    delete_image(ObjectId(image_id))
    flash('Image record deleted from database.', 'success')

    return redirect(url_for('profile'))



# Logout the user
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
