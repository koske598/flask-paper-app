import os
from os.path import join, dirname
from dotenv import load_dotenv
import sqlite3
from pathlib import Path

load_dotenv(verbose=True, override=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

FLASK_APP = os.environ.get("FLASK_APP")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
CORE_API_KEY = os.environ.get("CORE_API_KEY")
SQLALCHEMY_LOCAL_DATABASE_URI = os.environ.get("SQLALCHEMY_LOCAL_DATABASE_URI")
SQLALCHEMY_LOCAL_DATABASE_SQLITE3_URI = f"sqlite:///{'local.sqlite'}"
SQLALCHEMY_TESTING_DATABASE_URI = os.environ.get("SQLALCHEMY_TESTING_DATABASE_URI")
