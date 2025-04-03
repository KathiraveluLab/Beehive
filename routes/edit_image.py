from flask import Blueprint, flash, session, request, redirect, url_for
from bson import ObjectId
from Database.userdatahandler import update_image

edit_image_pb = Blueprint('edit_image', __name__)

# Edit images uploaded by the user
@edit_image_pb.route('/edit/<image_id>', methods=['POST'])
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