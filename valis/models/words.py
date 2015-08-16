
from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, subqueryload
from flask.ext.sqlalchemy import BaseQuery

from ..utils import OrderedDefaultDict
from ..context import db
import languages, definitions, keyword_mappings

class Query(BaseQuery):

    def filtered(self, language_code=None, word=None, word_prefix=None, word_suffix=None,\
                 user=None, valsi_type=None, after_word=None):
        query = self
        if language_code:
            query = query.\
                    join(languages.Language).\
                    filter(languages.Language.tag == language_code)
        if word:
            query = query.filter(Word.word == word)
        else:
            if word_prefix:
                query = query.filter(Word.word.startswith(word_prefix))
            if word_suffix:
                query = query.filter(Word.word.endswith(word_suffix))
            if after_word:
                query = query.filter(Word.word > after_word)
        return query

    def by_word_and_language(self, word_id, word, language_code):
        return self.\
                filter(Word.wordid == word_id, Word.word == word).\
                join(languages.Language).\
                filter(languages.Language.tag == language_code)

    def ordered(self, limit=None):
        query = self.order_by(Word.word, Word.wordid)
        if limit:
            query = query.limit(limit)
        return query

    def fully_loaded(self):
        return self.\
                options(joinedload(Word.language),
                        joinedload(Word.user),
                        subqueryload(Word.keyword_mappings).\
                                joinedload(keyword_mappings.KeywordMapping.definition).\
                                joinedload(definitions.Definition.valsi, definitions.Definition.language))

class Word(db.Model):

    query_class = Query
    __tablename__ = "natlangwords"
    __table_args__ = { "extend_existing": True }

    userid = Column(ForeignKey("users.userid"))

    language = db.relationship("Language",
            backref=db.backref("words", lazy="dynamic"))
    user = db.relationship("User", lazy="joined",
            backref=db.backref("words", lazy="dynamic"))

    @classmethod
    def fetch_words_and_count(cls, limit=None, **kwargs):
        words = cls.fetch_words(limit=limit, **kwargs)
        count = cls.fetch_words_count(**kwargs)
        return words, count

    @classmethod
    def fetch_words(cls, limit=None, **kwargs):
        query = cls.query.\
                filtered(**kwargs).\
                ordered(limit=limit).\
                fully_loaded()
        return query.all()

    @classmethod
    def fetch_words_count(cls, **kwargs):
        query = cls.query.filtered(**kwargs)
        return query.count()

    @classmethod
    def fetch_word(cls, language_code, word, word_id):
        return cls.query.\
                by_word_and_language(word_id, word, language_code).\
                fully_loaded().\
                first()

    @property
    def updated_at(self):
        return None if self.time == 0 else datetime.fromtimestamp(self.time)

    @property
    def language_tag(self):
        language = self.language
        return language.tag

    def keywords(self):
        return self._build_keyword_dictionary(self.keyword_mappings)

    @staticmethod
    def _build_keyword_dictionary(mappings):
        mapping_dictionary = OrderedDefaultDict()
        mapping_dictionary.default_factory = list
        for mapping in mappings:
            mapping_dictionary[mapping.place].append(mapping.definition)
        return mapping_dictionary

    def __repr__(self):
        return '<Word %d: "%s">' % (self.wordid, self.word.encode("utf-8"))

