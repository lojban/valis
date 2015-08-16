
from sqlalchemy import Column, Integer

from ..context import db
import languages, users

class Etymology(db.Model):

    __tablename__  = "etymology"
    __table_args__ = { "extend_existing": True }

    etymologyid = Column(Integer, primary_key=True)

    valsi = db.relationship("Valsi",
                            innerjoin=True,
                            backref=db.backref("etymologies"))

    language = db.relationship(languages.Language,
                               innerjoin=True)

    user = db.relationship(users.User,
                           backref=db.backref("etymologies", lazy="dynamic"))

    @property
    def language_tag(self):
        return self.language.tag if self.language else None

    def __repr__(self):
        return '<Etymology %d: "%s">' % (self.etymologyid, self.content.encode("utf-8"))

