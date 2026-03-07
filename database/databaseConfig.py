import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient, TEXT
from utils.logger import Logger

logger = Logger.get_logger("databaseConfig")

load_dotenv(find_dotenv())

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
    dbclient = MongoClient(connectionString)
    # Test the connection
    dbclient.admin.command("ping")
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error("Failed to connect to MongoDB", exc_info=True)
    logger.info("Attempting to connect to local MongoDB as fallback...")
    connectionString = "mongodb://localhost:27017/"
    dbclient = MongoClient(connectionString)
    dbclient.admin.command("ping")
    logger.info("Connected to local MongoDB")

beehive = dbclient.beehive
db = beehive

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
            logger.info("Text index created on image collection")
        else:
            logger.debug("Text index already exists on image collection")
        # Ensure an index exists for OTP verification queries to keep lookups fast
        try:
            otp_collection = beehive.email_otps
            otp_indexes = otp_collection.index_information()
            if 'email_verified_idx' not in otp_indexes:
                otp_collection.create_index(
                    [("email", 1), ("verified", 1), ("verified_at", -1)],
                    name='email_verified_idx',
                )
                logger.info("Created index on email_otps (email, verified, verified_at)")
            else:
                logger.debug("email_verified_idx already exists on email_otps")
        except Exception as ie:
            logger.error(f"Error creating email_otps index: {ie}")
    except Exception as e:
        logger.error(f"Error creating text index: {str(e)}")
