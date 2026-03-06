import os
import pytest
from app import app as flask_app

os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret-key-minimum-32-chars-long-for-pytest')

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-minimum-32-chars-long-for-pytest",
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
