import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient, TEXT
from utils.logger import Logger

logger = Logger.get_logger("databaseConfig")

load_dotenv(find_dotenv())

_client = None

def get_db():
    global _client
    if _client is not None:
        return _client.beehive

    connectionString = os.environ.get("MONGODB_URI")

    # Fallback to local MongoDB if connection string is not properly configured
    if (
        not connectionString
        or "username:password" in connectionString
        or connectionString == "mongodb+srv://username:password@cluster.mongodb.net/"
    ):
        logger.warning(
            "MONGODB_URI not properly configured, using local MongoDB"
        )
        connectionString = "mongodb://localhost:27017/"

    try:
        _client = MongoClient(connectionString)
        # Test the connection
        _client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error("Failed to connect to MongoDB", exc_info=True)
        logger.info("Attempting to connect to local MongoDB as fallback...")
        connectionString = "mongodb://localhost:27017/"
        _client = MongoClient(connectionString)
        _client.admin.command("ping")
        logger.info("Connected to local MongoDB")

    return _client.beehive

def get_beehive_user_collection():
    return get_db().users


def get_beehive_image_collection():
    return get_db().images


def get_beehive_admin_collection():
    return get_db().admins


def get_beehive_notification_collection():
    return get_db().notifications


def get_beehive_message_collection():
    return get_db().messages


def initialize_text_index():
    try:
        image_collection = get_beehive_image_collection()
        existing_indexes = image_collection.index_information()
        
        if 'title_text_description_text' not in existing_indexes:
            image_collection.create_index([
                ('title', TEXT),
                ('description', TEXT)
            ], name='title_text_description_text')
            logger.info("Text index created on image collection")
        else:
            logger.debug("Text index already exists on image collection")
    except Exception as e:
        logger.error(f"Error creating text index: {str(e)}")
