from flask import Blueprint, session, flash, redirect, url_for, current_app
from Database.userdatahandler import get_image_by_id, delete_image
from bson import ObjectId
import os

delete_image_pb = Blueprint('delete_image', __name__)

# Delete images uploaded by the user
@delete_image_pb.route('/delete/<image_id>')
def delete_image(image_id):

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
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                flash(f'Image file deleted: {image["filename"]}', 'success')
            except OSError as e:
                flash(f'Error deleting image file: {str(e)}', 'danger')
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