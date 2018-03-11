import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'src.core.config.DevelopmentConfig'
)
app.config.from_object(app_settings)
login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from core.control import blueprint

app.register_blueprint(blueprint)

