import base64
import datetime
import json
import os
import pathlib
import re
import sys
from functools import wraps

import bcrypt
import fitz
import google.auth.transport.requests
import requests
from bson import ObjectId
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from PIL import Image
from pip._vendor import cachecontrol
from werkzeug.utils import secure_filename

from Database import userdatahandler
from Database.admindatahandler import check_admin_available, create_admin, is_admin
from Database.userdatahandler import (
    create_google_user,
    create_user,
    delete_image,
    get_currentuser_from_session,
    get_image_by_id,
    get_images_by_user,
    get_password_by_username,
    get_user_by_email,
    get_user_by_username,
    is_email_available,
    is_username_available,
    isValidEmail,
    save_image,
    todays_images,
    total_images,
    update_image,
)
from usersutils import valid_username

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from OAuth.config import ALLOWED_EMAILS, GOOGLE_CLIENT_ID

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "heif", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = "beehive"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["PDF_THUMBNAIL_FOLDER"] = "static/uploads/thumbnails/"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://127.0.0.1:5000/admin/login/callback",
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()

    return wrapper


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Admin authentication via Google
            if "google_id" in session:
                if required_role == "admin" and not is_admin():
                    return render_template("403.html")

            # Regular user authentication - either via traditional login or Google SSO
            elif "username" in session:
                user = get_user_by_username(session["username"])

                if user is None:
                    print("User not found in session!")
                    return render_template("403.html")

                if user.get("role") != required_role:
                    return render_template("403.html")
            else:
                return render_template("403.html")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Login the user
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)

        if user:
            # Check if this is a Google authenticated user (has no password)
            if "google_id" in user:
                flash(
                    'This account uses Google Sign-In. Please use the "Sign in with Google" button.',
                    "info",
                )
                return render_template("login.html")

            stored_password = user.get("password")

            if stored_password:
                # Check if stored password is hashed
                if isinstance(stored_password, bytes) and stored_password.startswith(
                    b"$2b$"
                ):
                    # Handle hashed password
                    is_valid = bcrypt.checkpw(password.encode("utf-8"), stored_password)
                else:
                    # For plain text password
                    is_valid = stored_password == password

                if is_valid:
                    session["username"] = username

                    # Check for email field with safe handling
                    user_email = user.get("email")
                    if user_email:
                        session["email"] = user_email

                        # Check if this user's email is in ALLOWED_EMAILS
                        if user_email in ALLOWED_EMAILS:
                            # If they're an admin, check if they exist in admin collection
                            google_id = user.get("google_id", f"local_{username}")
                            if check_admin_available(google_id):
                                # Safely get user's name
                                first_name = user.get("first_name", "")
                                last_name = user.get("last_name", "")
                                full_name = f"{first_name} {last_name}".strip()
                                if not full_name:
                                    full_name = (
                                        username  # Use username if no name available
                                    )

                                create_admin(
                                    full_name,
                                    user_email,
                                    google_id,
                                    datetime.datetime.now(),
                                )
                            session["google_id"] = (
                                google_id  # Set google_id for admin authorization
                            )
                            flash("Login successful as admin!", "success")
                            return redirect(url_for("protected_area"))

                    # Default path if not admin or email missing
                    flash("Login successful!", "success")
                    return redirect(url_for("profile"))

        flash("Invalid credentials, please try again.", "danger")
    return render_template("login.html")


@app.route("/login/google")
def login_google():
    # Create a flow instance for user authentication
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
        redirect_uri="http://127.0.0.1:5000/login/google/callback",
    )

    authorization_url, state = user_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/login/google/callback")
def user_authorize():
    # Create a flow instance for the callback
    user_flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
        redirect_uri="http://127.0.0.1:5000/login/google/callback",
    )

    user_flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = user_flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    # Check if this is an admin email
    if session["email"] in ALLOWED_EMAILS:
        if check_admin_available(session["google_id"]):
            create_admin(
                session["name"],
                session["email"],
                session["google_id"],
                datetime.datetime.now(),
            )
        return redirect("/admin")
    else:
        # Handle regular user login via Google
        user = get_user_by_email(session["email"])

        if user:
            # User exists, set session and redirect to profile
            session["username"] = user["username"]
            flash("Login successful via Google!", "success")
            return redirect(url_for("profile"))
        else:
            # User doesn't exist yet
            session["google_login_pending"] = True
            flash(
                "No account exists with this email. Would you like to create one?",
                "info",
            )
            return redirect(url_for("google_register"))


# Add this new route to handle Google registrations
@app.route("/register/google", methods=["GET", "POST"])
def google_register():
    if "google_login_pending" not in session or "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Process registration form
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        username = request.form["username"]
        email = session["email"]  # Use email from Google
        google_id = session["google_id"]

        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        else:
            if is_username_available(username):
                account_created_at = datetime.datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )
                # Create user without password since they'll login with Google
                create_google_user(
                    first_name,
                    last_name,
                    email,
                    username,
                    google_id,
                    account_created_at,
                )

                # Set session and redirect
                session["username"] = username
                session.pop("google_login_pending", None)
                flash("Registration successful!", "success")
                return redirect(url_for("profile"))
            else:
                flash("This Username is already taken.", "danger")

    return render_template("google_register.html")


# Register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        security_question = request.form["security_question"]
        custom_question = request.form.get("custom_security_question")
        security_answer = request.form["security_answer"]
        account_created_at = None

        final_question = custom_question if custom_question else security_question

        if not valid_username.is_valid_username(username):
            flash("Username doesn't follow the rules", "danger")
        elif password != confirm_password:
            flash("Passwords do not match, please try again.", "danger")
        else:
            if (
                isValidEmail(email)
                and is_email_available(email)
                and is_username_available(username)
            ):
                if is_username_available(username):
                    account_created_at = datetime.datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    )
                    create_user(
                        first_name,
                        last_name,
                        email,
                        username,
                        password,
                        final_question,
                        security_answer,
                        account_created_at,
                    )
                    flash("Registration successful!", "success")
                    return redirect(url_for("login"))
                else:
                    flash("This Username already taken.", "danger")
            else:
                flash("This Email is already in use!", "danger")

    return render_template("register.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        security_answer = request.form.get("security_answer")
        new_password = request.form.get("new_password")
        user = get_user_by_username(username)
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("forgot_password"))

        # Verify the security answer
        if not bcrypt.checkpw(security_answer.encode("utf-8"), user["security_answer"]):
            flash("Incorrect security answer!", "danger")
            return redirect(url_for("forgot_password"))

        # Hash the new password
        from Database.userdatahandler import update_password

        update_password(user["_id"], new_password)

        flash("Password reset successful!", "success")
        return redirect(url_for("login"))

    return render_template("forgotpassword.html")


@app.route("/get_security_question", methods=["GET"])
def get_security_question():
    username = request.args.get("username")
    user = get_user_by_username(username)

    if user:
        return jsonify({"question": user["security_question"]})
    else:
        return jsonify({"question": None})  # Handle user not found case


# Display the user's profile page
@app.route("/profile")
def profile():
    if "username" not in session:
        flash("Please log in to access the profile page.", "danger")
        return redirect(url_for("login"))

    username = session["username"]
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    images = get_images_by_user(username)  # Fetch images uploaded by the user

    return render_template(
        "profile.html",
        username=user["username"],
        full_name=f"{user['first_name']} {user['last_name']}",
        images=images,
        user_dp=user.get("profile_photo"),  # Pass profile photo to template
    )


@app.route("/upload", methods=["POST"])
def upload_images():
    if "username" not in session:
        flash("Please log in to upload images.", "danger")
        return redirect(url_for("login"))

    user = get_user_by_username(session["username"])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    files = request.files.getlist("files")  # Supports multiple file uploads
    title = request.form.get("title", "")
    sentiment = request.form.get("sentiment")
    description = request.form.get("description", "")
    audio_data = request.form.get("audioData")

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

            # Handle audio file if provided
            audio_filename = None
            if audio_data:
                audio_filename = f"{secure_filename(title)}.wav"
                audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_filename)
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                audio_binary = base64.b64decode(audio_data.split(",")[1])
                with open(audio_path, "wb") as f:
                    f.write(audio_binary)

        time_created = datetime.datetime.now()
        save_image(
            user["username"],
            filename,
            title,
            description,
            time_created,
            audio_filename,
            sentiment,
        )
        flash("Image uploaded successfully!", "success")

        # Generate PDF thumbnail if applicable
        if filename.lower().endswith(".pdf"):
            generate_pdf_thumbnail(filepath, filename)

        else:
            flash("Invalid file type or no file selected.", "danger")

    return redirect(url_for("profile"))


@app.route("/upload_profile_photo", methods=["POST"])
def upload_profile_photo():
    if "username" not in session:
        flash("Please log in to update your profile photo.", "danger")
        return redirect(url_for("login"))

    username = session["username"]
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if "profile_photo" not in request.files:
        flash("No file selected.", "danger")
        return redirect(url_for("profile"))

    file = request.files["profile_photo"]

    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("profile"))

    if file and allowed_file(file.filename):
        filename = f"{username}_profile.{file.filename.rsplit('.', 1)[1].lower()}"
        upload_folder = os.path.join(app.config["UPLOAD_FOLDER"], "profile")

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Create missing directories

        filepath = os.path.join(upload_folder, filename)

        # Remove old profile photo if it exists
        if user.get("profile_photo"):
            old_filepath = os.path.join(
                app.config["UPLOAD_FOLDER"], "profile", user["profile_photo"]
            )
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Save the new file
        file.save(filepath)

        # Update user record in database with the new profile photo filename
        userdatahandler.update_profile_photo(username, filename)

        flash("Profile photo updated successfully!", "success")
    else:
        flash(
            "Invalid file type. Only jpg, jpeg, png, and gif files are allowed.",
            "danger",
        )

    return redirect(url_for("profile"))


# generate thumbnail for the pdf
def generate_pdf_thumbnail(pdf_path, filename):
    """Generate an image from the first page of a PDF using PyMuPDF."""
    # Ensure the thumbnails directory exists
    thumbnails_dir = os.path.join(app.config["UPLOAD_FOLDER"], "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)

    pdf_document = fitz.open(pdf_path)

    # select only the first page for the thumbnail
    first_page = pdf_document.load_page(0)

    zoom = 2  # Increase for higher resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = first_page.get_pixmap(matrix=mat)

    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    thumbnail_filename = filename.replace(".pdf", ".jpg")
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    image.save(thumbnail_path, "JPEG")

    return thumbnail_path


# Edit images uploaded by the user
@app.route("/edit/<image_id>", methods=["POST"])
def edit_image(image_id):

    if "username" in session or "google_id" in session:
        title = request.form["title"]
        description = request.form["description"]

        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            flash(f"Invalid image ID format: {str(e)}", "danger")
            return redirect(url_for("profile"))

        update_image(image_id, title, description)
        flash("Image updated successfully!", "success")
        if "username" in session:
            return redirect(url_for("profile"))
        elif "google_id" in session:
            return redirect(url_for("getallusers"))
        return redirect(url_for("login"))
    else:
        flash("Please log in to edit images.", "danger")
        return redirect(url_for("login"))


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# Delete images uploaded by the user
@app.route("/delete/<image_id>")
def delete_image_route(image_id):

    if "username" in session or "google_id" in session:

        try:
            image_id = ObjectId(image_id)
        except Exception as e:
            flash(f"Invalid image ID format: {str(e)}", "danger")
            return redirect(url_for("profile"))

        image = get_image_by_id(image_id)
        if not image:
            flash("Image not found.", "danger")
            return redirect(url_for("profile"))
        # Delete image file from upload directory
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], image["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
            flash(f'Image file deleted: {image["filename"]}', "success")
        else:
            flash("Image file not found in upload directory.", "danger")

        # Delete image record from database
        delete_image(image_id)
        flash("Image record deleted from database.", "success")
        if "username" in session:
            return redirect(url_for("profile"))
        elif "google_id" in session:
            return redirect(url_for("getallusers"))
        return redirect(url_for("login"))
    else:
        flash("Please log in to delete images.", "danger")
        return redirect(url_for("login"))


@app.route("/change-username", methods=["GET", "POST"])
def change_username():
    username = session["username"]
    users_collection = get_user_by_username(username)
    user_id = users_collection.get("_id")
    if request.method == "POST":
        new_username = request.form.get("new_username")

        # Check if username already exists
        from Database.userdatahandler import is_username_available

        if not is_username_available(new_username):
            flash("Username already taken!", "danger")
            return redirect(url_for("change_username"))

        from Database.userdatahandler import update_username

        update_username(user_id, new_username)
        session["username"] = new_username
        flash("Username updated successfully!", "success")

    return render_template("profile.html")


@app.route("/change-email", methods=["GET", "POST"])
def change_email():

    username = session["username"]
    users_collection = get_user_by_username(username)
    user_id = users_collection.get("_id")

    if request.method == "POST":
        new_email = request.form.get("new_email")

        from Database.userdatahandler import update_email

        update_email(user_id, new_email)
        flash("Email updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html")


@app.route("/change-password", methods=["POST"])
def change_password():

    username = session["username"]
    users_collection = get_user_by_username(username)
    user_id = users_collection.get("_id")

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    stored_password = users_collection["password"]

    # Verify the current password
    if not bcrypt.checkpw(current_password.encode("utf-8"), stored_password):
        flash("Current password is incorrect!", "danger")
        return redirect(url_for("profile"))

    from Database.userdatahandler import update_password

    update_password(user_id, new_password)

    flash("Password updated successfully!", "success")
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    # Clear all user session data
    session.pop("username", None)
    session.pop("google_id", None)
    session.pop("name", None)
    session.pop("email", None)
    session.pop("google_login_pending", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# Admin routes


@app.route("/signingoogle")
def signingoogle():
    return render_template("signingoogle.html")


@app.route("/admin/login")
def admin_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/admin/login/callback")
def authorize():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    if session["email"] in ALLOWED_EMAILS:
        if check_admin_available(session["google_id"]):
            create_admin(
                session["name"],
                session["email"],
                session["google_id"],
                datetime.datetime.now(),
            )
        with open("user_info.json", "w") as json_file:
            json.dump(session, json_file, indent=4)
        return redirect("/admin")
    else:
        return render_template("403.html")


@app.route("/admin")
@role_required("admin")
@login_is_required
def protected_area():
    admin_name = session.get("name")
    google_id = session.get("google_id")
    total_img = total_images()
    todays_image = todays_images()

    # Get admin profile photo
    from Database.admindatahandler import get_admin_by_google_id

    admin = get_admin_by_google_id(google_id)
    admin_photo = admin.get("profile_photo") if admin else None

    return render_template(
        "admin.html",
        admin_name=admin_name,
        total_img=total_img,
        todays_image=todays_image,
        admin_photo=admin_photo,
    )


@login_is_required
@role_required("admin")
@app.route("/admin/logout")
def adminlogout():
    session.clear()
    return redirect("/")


@app.route("/admin/users")
@role_required("admin")
def getallusers():
    users = userdatahandler.getallusers()
    return render_template("users.html", users=users)


@app.route("/admin/users/<username>")
@role_required("admin")
def user_images_show(username):
    user = get_user_by_username(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("getallusers"))

    images = get_images_by_user(username)
    return render_template(
        "user_images.html",
        username=username,
        images=images,
        full_name=f"{user['first_name']} {user['last_name']}",
    )


@app.route("/admin/reset_password", methods=["POST"])
def admin_reset_password():

    username = request.form.get("username")
    new_password = request.form.get("new_password")

    # Check if user exists
    user = get_user_by_username(username)
    if not user:
        flash("User not found!", "danger")
        return jsonify({"success": False, "message": "User not found!"})

    from Database.userdatahandler import update_password

    update_password(user["_id"], new_password)

    flash(f"Password for {username} reset successfully!", "success")
    return jsonify({"success": True, "redirect_url": url_for("getallusers")})


@app.route("/upload_admin_profile_photo", methods=["POST"])
def upload_admin_profile_photo():
    if "google_id" not in session:
        flash("Please log in to update your profile photo.", "danger")
        return redirect(url_for("admin_login"))

    # Manually check for admin role
    from Database.admindatahandler import is_admin

    if not is_admin():
        return render_template("403.html")

    google_id = session["google_id"]

    if "profile_photo" not in request.files:
        flash("No file selected.", "danger")
        return redirect("/admin")

    file = request.files["profile_photo"]

    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect("/admin")

    if file and allowed_file(file.filename):
        filename = (
            f"admin_{google_id}_profile.{file.filename.rsplit('.', 1)[1].lower()}"
        )
        profile_dir = os.path.join(app.config["UPLOAD_FOLDER"], "profile")

        # Create directory if it doesn't exist
        os.makedirs(profile_dir, exist_ok=True)

        filepath = os.path.join(profile_dir, filename)

        # Get admin data to check if old profile photo exists
        from Database.admindatahandler import get_admin_by_google_id

        admin = get_admin_by_google_id(google_id)

        # Remove old profile photo if it exists
        if admin and admin.get("profile_photo"):
            old_filepath = os.path.join(profile_dir, admin["profile_photo"])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Save the new file
        file.save(filepath)

        # Update admin record in database
        from Database.admindatahandler import update_admin_profile_photo

        update_admin_profile_photo(google_id, filename)

        flash("Profile photo updated successfully!", "success")
    else:
        flash(
            "Invalid file type. Only jpg, jpeg, png, and gif files are allowed.",
            "danger",
        )

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)
