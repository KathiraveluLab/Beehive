from flask import session, abort, render_template
from functools import wraps
from Database.userdatahandler import get_user_by_username
from Database.admindatahandler import is_admin


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  
        return function(*args, **kwargs)  # Pass args/kwargs properly

    return wrapper

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Admin authentication via Google
            if "google_id" in session:
                if required_role == 'admin' and not is_admin():
                    return render_template('403.html')
                    
            # Regular user authentication - either via traditional login or Google SSO
            elif "username" in session:
                user = get_user_by_username(session["username"])
                
                if user is None:
                    print("User not found in session!")
                    return render_template('403.html')  

                if user.get('role') != required_role:
                    return render_template('403.html')
            else:
                return render_template('403.html')

            return func(*args, **kwargs)

        return wrapper
    return decorator
