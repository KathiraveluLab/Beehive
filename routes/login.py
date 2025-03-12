from flask import Blueprint, request, flash, render_template, session, redirect, url_for
from Database.admindatahandler import check_admin_available, create_admin
from auth.OAuth.config import ALLOWED_EMAILS
import bcrypt
import datetime

from Database.userdatahandler import (
    isValidEmail, 
    is_email_available, 
    is_username_available,
    create_user,
    create_google_user,
    get_user_by_username,
    )

login_pb = Blueprint('login', __name__)

# Login the user
@login_pb.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user:
            # Check if this is a Google authenticated user (has no password)
            if 'google_id' in user:
                flash('This account uses Google Sign-In. Please use the "Sign in with Google" button.', 'info')
                return render_template("login.html")
                
            stored_password = user.get('password')
            
            if stored_password:
                # Check if stored password is hashed
                if isinstance(stored_password, bytes) and stored_password.startswith(b'$2b$'):
                    # Handle hashed password
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password)
                else:
                    # For plain text password
                    is_valid = (stored_password == password)
                
                if is_valid:
                    session['username'] = username
                    
                    # Check for email field with safe handling
                    user_email = user.get('email')
                    if user_email:
                        session['email'] = user_email
                        
                        # Check if this user's email is in ALLOWED_EMAILS
                        if user_email in ALLOWED_EMAILS:
                            # If they're an admin, check if they exist in admin collection
                            google_id = user.get('google_id', f"local_{username}")
                            if check_admin_available(google_id):
                                # Safely get user's name
                                first_name = user.get('first_name', '')
                                last_name = user.get('last_name', '')
                                full_name = f"{first_name} {last_name}".strip()
                                if not full_name:
                                    full_name = username  # Use username if no name available
                                    
                                create_admin(full_name, user_email, google_id, datetime.datetime.now())
                            session["google_id"] = google_id  # Set google_id for admin authorization
                            flash('Login successful as admin!', 'success')
                            return redirect(url_for("protected_area"))
                    
                    # Default path if not admin or email missing
                    flash('Login successful!', 'success')
                    return redirect(url_for("profile.profile"))
                    
        flash('Invalid credentials, please try again.', 'danger')
    return render_template("login.html")
