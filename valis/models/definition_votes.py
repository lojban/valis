
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy.sql import func

from ..context import db
import languages, valsi, users

class Query(BaseQuery):

    def sum_for_language_tag_and_valsi_word(self, language_code, word):
        query = self.\
                by_language_tag(language_code).\
                by_valsi_word(word)
        return query.\
                with_entities(DefinitionVote.definitionid, self.summed_value_as_score()).\
                group_by(DefinitionVote.definitionid, DefinitionVote.langid)

    def by_language_tag(self, language_code):
        return self.\
                join(languages.Language).\
                filter_by(tag=language_code)

    def by_valsi_word(self, word):
        return self.\
                join(valsi.Valsi).\
                filter_by(word=word)

    @staticmethod
    def summed_value_as_score():
        return func.sum(DefinitionVote.value).label("score")

    def sum_for_definition_id(self, definition_id):
        return self.\
                by_definition_id(definition_id).\
                with_entities(self.summed_value_as_score()).\
                group_by(DefinitionVote.definitionid)

    def by_definition_id(self, definition_id):
        return self.\
                filter(DefinitionVote.definitionid == definition_id)

class DefinitionVote(db.Model):

    query_class = Query

    __table__ = db.Model.metadata.tables["definitionvotes"]

    definition = db.relationship("Definition",
                                 innerjoin=True,
                                 backref=db.backref("definition_votes", lazy="dynamic"))

    user = db.relationship(users.User,
                           innerjoin=True,
                           backref=db.backref("definition_votes", lazy="dynamic"))

    @classmethod
    def sum_for_language_and_word(cls, language_code, word):
        query = cls.query.\
                sum_for_language_tag_and_valsi_word(language_code, word).\
                order_by(cls.query.summed_value_as_score().desc())
        return query.all()

    @classmethod
    def sum_for_definition_id(cls, definition_id):
        row = cls.query.\
                sum_for_definition_id(definition_id).\
                first()
        return row.score if row else 0

    def __repr__(self):
        return '<DefinitionVote (Definition %d, user %d, value %d)>' %\
                (self.definitionid, self.userid, self.value)

