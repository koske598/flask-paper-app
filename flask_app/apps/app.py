from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from os.path import join, dirname
from apps.config import config_dict


load_dotenv(verbose=True, override=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.signup"
login_manager.login_message = ""

def create_app(config_key):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_key])
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{'local.sqlite'}"
    
    db.init_app(app)
    
    Migrate(app, db)
    csrf.init_app(app)
    
    login_manager.init_app(app)
    
    from apps.crud import views as crud_views
    from apps.auth import views as auth_views
    from apps.scrapy import views as sc_views
    
    app.register_blueprint(crud_views.crud, url_prefix="/crud")
    app.register_blueprint(auth_views.auth, url_prefix="/auth")
    app.register_blueprint(sc_views.sc)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    return app


def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404


def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500