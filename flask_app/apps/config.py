from pathlib import Path
import secrets
from dotenv import load_dotenv
import os
from apps import setting

basedir = Path(__file__).parent.parent
load_dotenv(verbose=True, override=True)
class BaseConfig:
    SECRET_KEY = secrets.token_urlsafe(32)
    WTF_CSRF_SECRET_KEY = secrets.token_urlsafe(40)


class LocalConfig(BaseConfig):
    SQLALCHEMY_LOCAL_DATABASE_URI = setting.SQLALCHEMY_LOCAL_DATABASE_SQLITE3_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=True


class TestingConfig(BaseConfig):
    SQLALCHEMY_TESTING_DATABASE_URI = setting.SQLALCHEMY_TESTING_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

config = {
    "testing": TestingConfig,
    "local": LocalConfig
}

config_dict = {
    "testing": TestingConfig,
    "local": LocalConfig
}