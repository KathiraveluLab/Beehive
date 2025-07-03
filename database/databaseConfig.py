from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient

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