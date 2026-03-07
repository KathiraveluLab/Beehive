import os
import pytest
from config import Config


def test_secret_key_loaded_from_environment():
    assert Config.SECRET_KEY is not None
    assert Config.SECRET_KEY == os.environ.get('FLASK_SECRET_KEY')


def test_secret_key_not_weak_default():
    assert Config.SECRET_KEY != 'beehive'
    assert Config.SECRET_KEY != 'beehive-secret-key'


def test_secret_key_minimum_length():
    assert len(Config.SECRET_KEY) >= 32


def test_jwt_secret_loaded_from_environment():
    assert Config.JWT_SECRET is not None
    assert Config.JWT_SECRET == os.environ.get('JWT_SECRET')


def test_validate_config_missing_flask_secret(monkeypatch):
    monkeypatch.setattr(Config, 'SECRET_KEY', None)
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_short_flask_secret(monkeypatch):
    monkeypatch.setattr(Config, 'SECRET_KEY', "short")
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_weak_flask_secret(monkeypatch):
    monkeypatch.setattr(Config, 'SECRET_KEY', "your_flask_secret_key_here_CHANGE_THIS")
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_missing_jwt_secret(monkeypatch):
    monkeypatch.setattr(Config, 'JWT_SECRET', None)
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_short_jwt_secret(monkeypatch):
    monkeypatch.setattr(Config, 'JWT_SECRET', "short")
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_missing_mongodb_uri(monkeypatch):
    monkeypatch.setattr(Config, 'MONGODB_URI', None)
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_invalid_mongodb_uri(monkeypatch):
    monkeypatch.setattr(Config, 'MONGODB_URI', "invalid://localhost")
    with pytest.raises(SystemExit):
        Config.validate_config()


def test_validate_config_missing_cors_origins(monkeypatch):
    monkeypatch.setattr(Config, 'CORS_ORIGINS', [])
    with pytest.raises(SystemExit):
        Config.validate_config()
