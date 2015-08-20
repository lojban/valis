
from flask.ext.sqlalchemy import BaseQuery

from ..context import db

class BestDefinition(db.Model):

    __table__ = db.Model.metadata.tables["valsibestdefinitions"]

    valsi = db.relationship("Valsi",
                            innerjoin=True,
                            backref=db.backref("best_definitions", lazy="dynamic"))

    language = db.relationship("Language",
                               innerjoin=True)

    definition = db.relationship("Definition",
                                 innerjoin=True,
                                 backref=db.backref("best"))

