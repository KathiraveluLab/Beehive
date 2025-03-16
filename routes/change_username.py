from flask import Blueprint, session, request, flash, redirect, url_for, render_template
from Database.userdatahandler import get_user_by_username

change_username_pb = Blueprint('change_username', __name__)

@change_username_pb.route('/change-username', methods=['GET', 'POST'])
def change_username():
    username = session['username']
    users_collection = get_user_by_username(username)
    user_id = users_collection.get('_id')
    if request.method == 'POST':
        new_username = request.form.get('new_username')

        # Check if username already exists
        from Database.userdatahandler import is_username_available
        if not is_username_available(new_username):
            flash("Username already taken!", "danger")
            return redirect(url_for('change_username'))

        from Database.userdatahandler import update_username
        update_username(user_id, new_username)
        session['username'] = new_username
        flash("Username updated successfully!", "success")
        

    return render_template('profile.html')