from datetime import date
import datetime
from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient

load_dotenv(find_dotenv())


connectionString = os.environ.get("MONGODB_CONNECTION_STRING")


dbclient = MongoClient(connectionString)

beehive = dbclient.beehive

beehive_user_collection = beehive.users


def create_user(firstname: str, lastname: str, email: str, username: str, password: str, accountcreatedtime: datetime):
    
    user_data = {
        "first_name" : firstname,
        "last_name" : lastname,
        "mail_id" : email,
        "username" : username,
        "password" : password,
        "account_created_at" : accountcreatedtime
    }
    user_inserted_id = beehive_user_collection.insert_one(user_data).inserted_id

def is_username_available(username: str):
    query= {
        "username" : username
    }

    count = beehive_user_collection.count_documents(query)
    return count == 0

def get_password_by_username(username: str):
    query = {
        "username" : username
    }
    user = beehive_user_collection.find_one(query)
    if user:
        return user.get("password")
    else:
        return "user not found!"


    