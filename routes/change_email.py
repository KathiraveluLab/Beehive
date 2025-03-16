from flask import Blueprint, session, request, url_for, flash, redirect, render_template
from Database.userdatahandler import get_user_by_username

change_email_pb = Blueprint('change_email', __name__)

@change_email_pb.route('/change-email', methods=['GET', 'POST'])
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