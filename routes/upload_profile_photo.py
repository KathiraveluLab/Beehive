from flask import Blueprint, session, flash, redirect, url_for, request, current_app
from Database.userdatahandler import get_user_by_username, update_profile_photo
from usersutils.allowd_files import allowed_file 
import os

upload_profile_photo_pb = Blueprint('upload_profile_photo', __name__)

@upload_profile_photo_pb.route('/upload_profile_photo', methods=['POST'])
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
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Create missing directories
        
        filepath = os.path.join(upload_folder, filename)
        
        # Remove old profile photo if it exists
        if user.get('profile_photo'):
            old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile', user['profile_photo'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Save the new file
        file.save(filepath)
        
        # Update user record in database with the new profile photo filename
        update_profile_photo(username, filename)
        
        flash('Profile photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Only jpg, jpeg, png, and gif files are allowed.', 'danger')
    
    return redirect(url_for('profile'))