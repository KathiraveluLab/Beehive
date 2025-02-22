from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
ALLOWED_EMAILS = os.getenv('ADMIN_EMAILS','').split(',')
