import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

class DatabaseConfig:
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    @classmethod
    def get_database(cls) -> Database:
        if cls._db is None:
            connection_string = os.environ.get("MONGODB_CONNECTION_STRING")
            if not connection_string:
                raise ValueError("MONGODB_CONNECTION_STRING environment variable is not set")
            cls._client = MongoClient(connection_string)
            cls._db = cls._client.get_database()
        return cls._db

    @classmethod
    def set_database(cls, db):
        cls._db = db
    
    @classmethod
    def get_beehive_user_collection(cls):
        return cls.get_database().beehive_user_collection
    
    @classmethod
    def get_beehive_image_collection(cls):
        return cls.get_database().beehive_image_collection
    
    @classmethod
    def get_beehive_admin_collection(cls):
        return cls.get_database().beehive_admin_collection
    
    @classmethod
    def reset(cls):
        """Reset the database connection - useful for testing"""
        if cls._client:
            cls._client.close()
        cls._client = None
        cls._db = None