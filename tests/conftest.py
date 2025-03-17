import os
import pytest
from pymongo import MongoClient
from app import app as flask_app
from Database.DatabaseConfig import DatabaseConfig


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Store original connection string
    original_conn = os.environ.get("MONGODB_CONNECTION_STRING")
    
    # Set test connection string
    os.environ["MONGODB_CONNECTION_STRING"] = "mongodb://localhost:27017/"
    
    # Reset the DatabaseConfig to ensure it uses the test connection string
    DatabaseConfig.reset()
    
    yield
    
    # Restore original connection string
    if original_conn:
        os.environ["MONGODB_CONNECTION_STRING"] = original_conn
    else:
        del os.environ["MONGODB_CONNECTION_STRING"]
    
    # Reset the DatabaseConfig again to ensure it will use the original connection string
    DatabaseConfig.reset()


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    flask_app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'localhost.localdomain',
        'WTF_CSRF_ENABLED': False  # Disable CSRF for testing
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
    # Reset any existing connection
    DatabaseConfig.reset()
    
    # Create new test client and database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["beehive_test"]
    
    # Set test database
    DatabaseConfig.set_database(db)
    
    # Clear test collections before each test
    db.users.delete_many({})
    db.images.delete_many({})
    db.admins.delete_many({})
    
    yield db
    
    # Drop the entire test database to ensure a clean state
    client.drop_database("beehive_test")
    
    # Close connection and reset config
    client.close()
    DatabaseConfig.reset() 