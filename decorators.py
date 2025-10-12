from functools import wraps
from flask import session, render_template
from database.admindatahandler import is_admin
from database.userdatahandler import get_user_by_username

# Shared decorators to prevent circular imports

def login_is_required(function):
    @wraps(function)
    def login_wrapper(*args, **kwargs):
        if "google_id" not in session:
            return "Unauthorized", 401
        else:
            return function()
    return login_wrapper


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Admin authentication via Google session
            if "google_id" in session:
                if required_role == 'admin' and not is_admin():
                    return render_template('403.html'), 403

            # Regular user authentication via username session
            elif "username" in session:
                user = get_user_by_username(session["username"])
                if user is None or user.get('role') != required_role:
                    return render_template('403.html'), 403
            
            else:
                return render_template('403.html'), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
