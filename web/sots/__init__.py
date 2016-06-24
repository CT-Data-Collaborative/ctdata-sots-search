from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from sots.config import BaseConfig as ConfigObject
app.config.from_object(ConfigObject)
if app.debug:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

db = SQLAlchemy(app)

from sots.models import *
from sots.views import *
