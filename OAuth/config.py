import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
raw_admin_emails = os.getenv("ADMIN_EMAILS", "")
ALLOWED_EMAILS = [
    email.strip() for email in raw_admin_emails.split(",") if email.strip()
]
