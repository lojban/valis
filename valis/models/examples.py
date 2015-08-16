
from sqlalchemy import Column, Integer, ForeignKey

from ..context import db
import users

class Example(db.Model):

    __tablename__  = "example"
    __table_args__ = { "extend_existing": True }

    exampleid    = Column(Integer, primary_key=True)
    definitionid = Column(ForeignKey("definitions.definitionid"))

    definition = db.relationship("Definition",
                                 innerjoin=True,
                                 backref=db.backref("examples",
                                                    order_by="Example.examplenum"))

    user = db.relationship(users.User,
                           backref=db.backref("examples", lazy="dynamic"))

    def __repr__(self):
        return '<Example %d: "%s">' % (self.exampleid, self.content.encode("utf-8"))

