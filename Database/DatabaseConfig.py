import os

from dotenv import find_dotenv, load_dotenv
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