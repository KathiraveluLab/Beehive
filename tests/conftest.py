from unittest.mock import patch

import mongomock
import pytest

from utils.jwt_auth import create_access_token

@pytest.fixture(scope="session", autouse=True)
def mongo_client_patch():
    with patch("pymongo.MongoClient", mongomock.MongoClient):
        yield


@pytest.fixture(scope="session")
def flask_app(mongo_client_patch):
    from app import app as _flask_app
    return _flask_app


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client.beehive
    with (
        patch("routes.auth.get_db", return_value=db),
        patch("routes.adminroutes.get_db", return_value=db),
        patch("database.databaseConfig.get_db", return_value=db),
        patch("database.userdatahandler.beehive_image_collection", db.images),
        patch("database.userdatahandler.beehive_user_collection", db.users),
        patch(
            "database.userdatahandler.beehive_notification_collection", db.notifications
        ),
    ):
        yield db




@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(user_id="mock_admin_id", role="admin")


@pytest.fixture
def app(flask_app):
    flask_app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "beehive",
            "JWT_SECRET": "test-jwt-secret",
        }
    )
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
