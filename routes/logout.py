from flask import session, flash, redirect, url_for, Blueprint

logout_pb = Blueprint('logout', __name__)

@logout_pb.route('/logout')
def logout():
    # Clear all user session data
    session.pop('username', None)
    session.pop('google_id', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('google_login_pending', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login.login'))