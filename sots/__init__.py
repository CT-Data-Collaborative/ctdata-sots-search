from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from opbeat.contrib.flask import Opbeat

app = Flask(__name__)
from sots.config import BaseConfig as ConfigObject
app.config.from_object(ConfigObject)
if app.debug == True:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
    toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)

opbeat = Opbeat(
    app,
    organization_id=ConfigObject.OPBEAT_ORG_ID,
    app_id=ConfigObject.OPBEAT_APP_ID,
    secret_token=ConfigObject.OPBEAT_SECRET,
)

from sots.models import *
from sots.views import *
