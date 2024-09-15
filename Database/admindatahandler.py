from datetime import datetime
import re

from Database import DatabaseConfig

beehive_admin_collection = DatabaseConfig.get_beehive_admin_collection()

def create_admin(name: str, email: str, google_id: str, accountcreatedtime: datetime):
    
    admin_data = {
        "name" : name,
        "mail_id" : email,
        "google_id" : google_id,
        "account_created_at" : accountcreatedtime,
        "role" : "admin"
    }
    admin_inserted_id = beehive_admin_collection.insert_one(admin_data).inserted_id

def check_admin_available(google_id: str):
    query = {
        "google_id" : google_id
    }

    count = beehive_admin_collection.count_documents(query)
    return count == 0