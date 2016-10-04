# config.py
import os

class BaseConfig(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = os.environ['DEBUG']
    FLASK_DEBUG = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_PORT = os.environ['DB_PORT']
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )
    OPBEAT_ORG_ID = os.environ['OPBEAT_ORGANIZATIONAL_ID']
    OPBEAT_APP_ID = os.environ['OPBEAT_APP_ID']
    OPBEAT_SECRET = os.environ['OPBEAT_SECRET_TOKEN']
    # pagination
    RESULTS_PER_PAGE = 25
    DEBUG_TB_PROFILER_ENABLED = os.environ['DEBUG']


class TestConfig(object):
    SECRET_KEY = 'changeme'
    DEBUG = True
    DB_NAME = 'postgres'
    DB_USER = 'postgres'
    DB_PASS = ''
    DB_SERVICE = '0.0.0.0'
    DB_PORT = '5432'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )