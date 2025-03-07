from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve environment variables with defaults
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Default for security

# Handle missing ADMIN_EMAILS
ADMIN_EMAILS_ENV = os.getenv("ADMIN_EMAILS", "")
ALLOWED_EMAILS = ADMIN_EMAILS_ENV.split(",") if ADMIN_EMAILS_ENV else []

# Debugging: Warn if critical variables are missing
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not REDIRECT_URI:
    print("⚠️ Warning: Missing Google OAuth credentials!")

if not FLASK_SECRET_KEY:
    print("⚠️ Warning: FLASK_SECRET_KEY is missing!")

if not ALLOWED_EMAILS:
    print("⚠️ Warning: No admin emails specified!")
