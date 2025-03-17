import os
import pytest
from pymongo import MongoClient
from app import app as flask_app
from Database.DatabaseConfig import DatabaseConfig


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    original_conn = os.environ.get("MONGODB_CONNECTION_STRING")
    os.environ["MONGODB_CONNECTION_STRING"] = "mongodb://localhost:27017/"
    DatabaseConfig.reset()
    
    yield
    
    if original_conn:
        os.environ["MONGODB_CONNECTION_STRING"] = original_conn
    else:
        del os.environ["MONGODB_CONNECTION_STRING"]
    DatabaseConfig.reset()


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    flask_app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'localhost.localdomain',
        'WTF_CSRF_ENABLED': False
    })
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create a test database connection."""
    DatabaseConfig.reset()
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client["beehive_test"]
    DatabaseConfig.set_database(db)
    
    db.users.delete_many({})
    db.images.delete_many({})
    db.admins.delete_many({})
    
    yield db
    
    client.drop_database("beehive_test")
    client.close()
    DatabaseConfig.reset()