import os
import pytest

TEST_SECRET_KEY = 'test-secret-key-minimum-32-chars-long-for-pytest'
os.environ['FLASK_SECRET_KEY'] = TEST_SECRET_KEY
os.environ['JWT_SECRET'] = TEST_SECRET_KEY

os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret-key-minimum-32-chars-long-for-pytest')

import pytest
from app import app as flask_app
@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": TEST_SECRET_KEY,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
