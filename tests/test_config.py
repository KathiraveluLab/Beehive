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


def test_validate_config_checks_secret_key():
    original_key = Config.SECRET_KEY
    
    Config.SECRET_KEY = None
    with pytest.raises(ValueError, match="FLASK_SECRET_KEY"):
        Config.validate_config()
    
    Config.SECRET_KEY = "short"
    with pytest.raises(ValueError, match="at least 32 characters"):
        Config.validate_config()
    
    Config.SECRET_KEY = "beehive"
    with pytest.raises(ValueError, match="default or example value"):
        Config.validate_config()
    
    Config.SECRET_KEY = original_key


def test_validate_config_checks_clerk_keys():
    original_clerk_key = Config.CLERK_SECRET_KEY
    original_clerk_issuer = Config.CLERK_ISSUER
    
    Config.CLERK_SECRET_KEY = None
    with pytest.raises(ValueError, match="CLERK_SECRET_KEY"):
        Config.validate_config()
    
    Config.CLERK_SECRET_KEY = original_clerk_key
    Config.CLERK_ISSUER = None
    with pytest.raises(ValueError, match="CLERK_ISSUER"):
        Config.validate_config()
    
    Config.CLERK_SECRET_KEY = original_clerk_key
    Config.CLERK_ISSUER = original_clerk_issuer
