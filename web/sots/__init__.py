from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from sots.config import BaseConfig as ConfigObject
app.config.from_object(ConfigObject)
db = SQLAlchemy(app)

from sots.models import *
from sots.views import *

if __name__ == "__main__":
    app.run(debug=True)