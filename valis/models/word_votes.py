
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy.sql import func

from ..context import db
import definitions

class Query(BaseQuery):

    def sum_for_language_tag_and_valsi_word(self, language_code, word):
        score = self.summed_value_as_score()
        return definitions.Definition.query.\
                by_language_tag_and_valsi_word(language_code, word).\
                join(definitions.Definition.word_votes).\
                with_entities(WordVote.definitionid, WordVote.place, WordVote.natlangwordid, score).\
                group_by(WordVote.definitionid, WordVote.place, WordVote.natlangwordid)

    @staticmethod
    def summed_value_as_score():
        return func.sum(WordVote.value).label("score")

    def sum_for_definition_id(self, definition_id):
        score = self.summed_value_as_score()
        return definitions.Definition.query.\
                filter_by(definitionid=definition_id).\
                join(definitions.Definition.word_votes).\
                with_entities(WordVote.definitionid, WordVote.place, WordVote.natlangwordid, score).\
                group_by(WordVote.definitionid, WordVote.place, WordVote.natlangwordid)

class WordVote(db.Model):

    query_class = Query

    __table__ = db.Model.metadata.tables["natlangwordvotes"]

    word = db.relationship("Word",
                           innerjoin=True,
                           backref=db.backref("word_votes", lazy="dynamic"))

    definition = db.relationship("Definition",
                                 innerjoin=True,
                                 backref=db.backref("word_votes", innerjoin=True))

    user = db.relationship("User",
                           innerjoin=True,
                           backref=db.backref("word_votes", lazy="dynamic"))

    @classmethod
    def sum_for_language_and_word(cls, language_code, word):
        query = cls.query.\
                sum_for_language_tag_and_valsi_word(language_code, word)
        return query.all()

    @classmethod
    def sum_for_definition_id(cls, definition_id):
        query = cls.query.\
                sum_for_definition_id(definition_id)
        return query.all()

    def __repr__(self):
        return '<WordVote (Definition %d, place %d, word %d, user %d, value %d)>' %\
                (self.definitionid, self.place, self.natlangwordid, self.userid, self.value)

