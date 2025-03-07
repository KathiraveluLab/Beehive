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
        if 'google_id' in session:
            admin = beehive_admin_collection.find_one({"google_id": session['google_id']})
            return admin is not None and admin.get("role") == "admin"
    except Exception as e:
        print(f"❌ Error checking admin status: {e}")
    return False
