import pytest
import mongomock
from unittest.mock import patch
from app import app as flask_app

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client.beehive
    with patch("routes.auth.get_db", return_value=db), \
         patch("routes.adminroutes.get_db", return_value=db), \
         patch("database.userdatahandler.beehive_image_collection", db.images), \
         patch("database.userdatahandler.beehive_user_collection", db.users):
        yield db

from utils.jwt_auth import create_access_token

@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(user_id="mock_admin_id", role="admin")

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "beehive",
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
