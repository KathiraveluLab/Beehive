from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient, TEXT

load_dotenv(find_dotenv())

connectionString = os.environ.get("MONGODB_CONNECTION_STRING")

dbclient = MongoClient(connectionString)

beehive = dbclient.beehive


def get_beehive_user_collection():
    return beehive.users

def get_beehive_image_collection():
    return beehive.images

def get_beehive_admin_collection():
    return beehive.admins

def get_beehive_notification_collection():
    return beehive.notifications

def get_beehive_message_collection():
    return beehive.messages

def initialize_text_index():
    try:
        image_collection = get_beehive_image_collection()
        existing_indexes = image_collection.index_information()
        
        if 'title_text_description_text' not in existing_indexes:
            image_collection.create_index([
                ('title', TEXT),
                ('description', TEXT)
            ], name='title_text_description_text')
            print("Text index created")
    except Exception as e:
        print(f"Error creating text index: {str(e)}")