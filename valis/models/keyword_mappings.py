
from ..context import db
from mixins import Annotated

class KeywordMapping(db.Model, Annotated):

    __table__ = db.Model.metadata.tables['keywordmapping']

    definition = db.relationship("Definition",
                                 innerjoin=True,
                                 backref=db.backref("keyword_mappings",
                                                    order_by="KeywordMapping.place"))
    word = db.relationship("Word",
                           innerjoin=True,
                           backref=db.backref("keyword_mappings"))

    def __repr__(self):
        return '<KeywordMapping (Definition %d, place %d, word %d)>' %\
                (self.definitionid, self.place, self.natlangwordid)

