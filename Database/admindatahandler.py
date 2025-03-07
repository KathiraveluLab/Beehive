from datetime import datetime
from flask import session
from Database import DatabaseConfig

# Get the admin collection from the database
beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()

if beehive_admin_collection is None:
    raise ValueError("❌ Database connection failed. Admin collection is unavailable.")

def create_admin(name: str, email: str, google_id: str, account_created_time: datetime):
    """Creates a new admin entry in the database."""
    try:
        admin_data = {
            "name": name,
            "mail_id": email,
            "google_id": google_id,
            "account_created_at": account_created_time,
            "role": "admin"
        }
        result = beehive_admin_collection.insert_one(admin_data)
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return None

def check_admin_available(google_id: str) -> bool:
    """Checks if an admin with the given Google ID exists."""
    try:
        return beehive_admin_collection.find_one({"google_id": google_id}) is None
    except Exception as e:
        print(f"❌ Error checking admin availability: {e}")
        return False

def is_admin() -> bool:
    """Checks if the current session user is an admin."""
    try:
        # Check admin based on google_id (for Google sign-in)
        if 'google_id' in session:
            admin = beehive_admin_collection.find_one({"google_id": session['google_id']})
            if admin and admin.get("role") == "admin":
                return True
        
        # Check admin based on email (for regular login)
        if 'email' in session:
            email = session['email']
            # Import ALLOWED_EMAILS list if not already available
            from OAuth.config import ALLOWED_EMAILS
            if email in ALLOWED_EMAILS:
                return True

    except Exception as e:
        print(f"❌ Error checking admin status: {e}")

    return False  # Default return if no admin role is found


def update_admin_profile_photo(google_id, filename):
    """Update the profile photo filename for an admin."""
    beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()
    beehive_admin_collection.update_one(
        {"google_id": google_id},
        {"$set": {"profile_photo": filename}}
    )

def get_admin_by_google_id(google_id):
    """Get admin details by Google ID."""
    beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()
    query = {
        "google_id": google_id
    }
    admin = beehive_admin_collection.find_one(query)
    return admin