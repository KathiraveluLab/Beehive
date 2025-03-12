from flask import Blueprint, flash, session, redirect, render_template, url_for
from Database.userdatahandler import (
    get_user_by_username,
    get_images_by_user
    )

profile_pb = Blueprint('profile', __name__)

# Display the user's profile page
@profile_pb.route('/profile')
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
        images=images,
        user_dp=user.get('profile_photo')  # Pass profile photo to template
    )