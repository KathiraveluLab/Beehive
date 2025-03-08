from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from usersutils import valid_username
from Database.userdatahandler import (
    isValidEmail, 
    is_email_available, 
    is_username_available,
    create_user,
    create_google_user
    )

import datetime

register_bp = Blueprint('register', __name__)


# Register a new user
@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_created_at = None

        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        elif password != confirm_password:
            flash('Passwords do not match, please try again.', 'danger')
        else:
                if isValidEmail(email) and is_email_available(email) and is_username_available(username):
                    if is_username_available(username):
                        account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                        create_user(first_name, last_name, email, username, password, account_created_at)
                        flash('Registration successful!', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('This Username already taken.', 'danger')
                else:
                    flash('This Email is already in use!', 'danger')


    return render_template("register.html")


# Add this new route to handle Google registrations
@register_bp.route('/register/google', methods=['GET', 'POST'])
def google_register():
    if "google_login_pending" not in session or "email" not in session:
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        # Process registration form
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        username = request.form['username']
        email = session["email"]  # Use email from Google
        google_id = session["google_id"]
        
        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        else:
            if is_username_available(username):
                account_created_at = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                # Create user without password since they'll login with Google
                create_google_user(first_name, last_name, email, username, google_id, account_created_at)
                
                # Set session and redirect
                session["username"] = username
                session.pop("google_login_pending", None)
                flash('Registration successful!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('This Username is already taken.', 'danger')
                
    return render_template("google_register.html")