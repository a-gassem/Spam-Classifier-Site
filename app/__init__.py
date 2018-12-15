from flask import Flask
from config import Config
from . import db

app = Flask(__name__)
app.config.from_object(Config)

#lets us define and access database
db.init_app(app)

from app import routes
