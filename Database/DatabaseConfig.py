import os
from pymongo import MongoClient

class DatabaseConfig:
    _instance = None
    _client = None
    _db = None
    
    @classmethod
    def get_database(cls):
        if cls._db is None:
            connection_string = os.environ.get("MONGODB_CONNECTION_STRING")
            cls._client = MongoClient(connection_string)
            cls._db = cls._client["beehive"]
        return cls._db
    
    @classmethod
    def set_database(cls, db):
        cls._db = db
    
    @classmethod
    def get_beehive_user_collection(cls):
        return cls.get_database()["users"]
    
    @classmethod
    def get_beehive_image_collection(cls):
        return cls.get_database()["images"]
    
    @classmethod
    def get_beehive_admin_collection(cls):
        return cls.get_database()["admins"]
    
    @classmethod
    def reset(cls):
        """Reset the database connection - useful for testing"""
        if cls._client:
            cls._client.close()
        cls._client = None
        cls._db = None