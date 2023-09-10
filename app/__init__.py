from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

subject_json_mapping = {
    'Python': 'python.json',
    'Network': 'network.json',
    'Git': 'git.json',
    'English': 'english.json',
    'SQL': 'sql.json'
}

from .routes import routes_file

from .models import User, Subject, Exam, Question
