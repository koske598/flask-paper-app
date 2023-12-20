from flask import Flask
import pytest
from apps.app import create_app, db
from apps.crud.models import User
from flask_app.apps.scrapy.models import UserKeyword
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def fixture_app():
    app = create_app('testing')
    
    app.app_context().push()
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    User.query.delete()
    
    try:
        UserKeyword.query.delete()
        
    except IntegrityError as e:
        #Handle the integrity error, e.g., log it or take appropriate action
        pass
    
    
    #shutil.rmtree(app.config)
    
    db.session.commit()

@pytest.fixture
def client(fixture_app: Flask):
    return fixture_app.test_client()