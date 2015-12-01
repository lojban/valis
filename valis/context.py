
import warnings

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.sqlalchemy import SQLAlchemy
import sqlalchemy

app = Flask(__name__)
db  = SQLAlchemy()

def configure(config):
    configure_application(config)
    configure_database()
    configure_json()
    configure_cors()

def configure_application(config):
    app.config.from_object(config)

def configure_database():
    db.init_app(app)
    db.app = app
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sqlalchemy.exc.SAWarning)
        #
        # Can't reflect expression-based and partial indexes:
        #
        #   valsi_lower_word,
        #   valsi_unique_word_nospaces,
        #   natlangwords_lower_word,
        #   natlangwords_unique_langid_word_null
        #
        db.reflect(app=app)

def configure_json():
    app.config['RESTFUL_JSON'] = {
        'sort_keys'    : False,
        'ensure_ascii' : False,
        'indent'       : 2
    }

def configure_cors():
    CORS(app, resources={
        r"/api/*" : { "origins" : "*" }
    })

