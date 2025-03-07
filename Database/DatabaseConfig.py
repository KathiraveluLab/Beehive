from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient

# Load environment variables
load_dotenv(find_dotenv())

# Retrieve MongoDB connection string from .env
connection_string = os.environ.get("MONGODB_CONNECTION_STRING")

if not connection_string:
    raise ValueError("Error: MONGODB_CONNECTION_STRING is not set in the .env file.")

try:
    # Establish MongoDB connection
    db_client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)  # 5s timeout
    db_client.server_info()  # Force connection check
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    db_client = None

# Database reference
if db_client:
    beehive_db = db_client.get_database("beehive")
else:
    beehive_db = None

# Collection access functions
def get_beehive_user_collection():
    if beehive_db:
        return beehive_db.get_collection("users")
    return None

def get_beehive_image_collection():
    if beehive_db:
        return beehive_db.get_collection("images")
    return None

def get_beehive_admin_collection():
    if beehive_db:
        return beehive_db.get_collection("admins")
    return None
