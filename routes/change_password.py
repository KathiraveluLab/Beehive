from flask import Blueprint, session, request, flash, url_for, redirect
from Database.userdatahandler import (
    get_user_by_username
)
import bcrypt


change_password_pb = Blueprint('password', __name__)

@change_password_pb.route('/change', methods=['POST'])
def change():

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