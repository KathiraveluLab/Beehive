from flask import Blueprint, request, flash, redirect, url_for, session, current_app
from usersutils.allowd_files import allowed_file
from werkzeug.utils import secure_filename
from Database.userdatahandler import (
    get_user_by_username,
)
import base64
import os

upload_pb = Blueprint('upload', __name__)

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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
    
    # Handle audio file if provided
    audio_filename = None
    if audio_data:
        audio_filename = f"{secure_filename(title)}.wav"
        audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        audio_binary = base64.b64decode(audio_data.split(',')[1])
        with open(audio_path, "wb") as f:
            f.write(audio_binary)