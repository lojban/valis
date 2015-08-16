
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app  = Flask(__name__)
db   = SQLAlchemy()

VERSION = '0.1.0'

def configure(config):
    configure_application(config)
    configure_database()
    configure_json()

def configure_application(config):
    app.config.from_object(config)

def configure_database():
    db.init_app(app)
    db.app = app
    db.reflect(app=app)

def configure_json():
    app.config['RESTFUL_JSON'] = {
        'sort_keys'    : False,
        'ensure_ascii' : False,
        'indent'       : 2
    }

