
from datetime import datetime
from collections import defaultdict, OrderedDict

from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy.orm import joinedload, contains_eager, subqueryload

from ..utils import OrderedDefaultDict
from ..context import db
from mixins import Annotated
import languages, valsi, users, words, examples, keyword_mappings, \
        definition_votes, word_votes

class Query(BaseQuery):

    def by_language_tag_and_valsi_word(self, language_code, word):
        query = self.\
                by_language_tag(language_code).\
                by_valsi_word(word)
        return query

    def by_language_tag(self, language_code):
        return self.\
                join(Definition.language).\
                filter(languages.Language.tag == language_code)

    def by_valsi_word(self, word):
        return self.\
                join(Definition.valsi).\
                filter(valsi.Valsi.word == word)

    def for_id(self, definition_id, language_code=None, word=None):
        query = self.\
                filter(Definition.definitionid == definition_id)
        if language_code:
            query = query.by_language_tag(language_code)
        if word:
            query = query.by_valsi_word(word)
        return query

    def fully_loaded_by_language_tag_and_valsi_word(self):
        return self.\
                options(contains_eager(Definition.language),
                        contains_eager(Definition.valsi),
                        joinedload(Definition.user),
                        subqueryload(Definition.keyword_mappings).\
                                joinedload(keyword_mappings.KeywordMapping.word).\
                                joinedload(words.Word.language, words.Word.user),
                        subqueryload(Definition.examples).\
                                joinedload(examples.Example.user))

    def best_by_language_tag_and_valsi_word(self, language_code, word):
        query = self.\
                by_language_tag(language_code).\
                by_valsi_word(word).\
                join(Definition.best)
        return query

class Definition(db.Model, Annotated):

    query_class = Query

    __table__ = db.Model.metadata.tables["definitions"]

    valsi = db.relationship("Valsi",
                            innerjoin=True,
                            backref=db.backref("definitions"))

    language  = db.relationship(languages.Language, innerjoin=True)

    user = db.relationship(users.User,
                           backref=db.backref("definitions", lazy="dynamic"))

    @classmethod
    def fetch_by_language_and_word_with_scores(cls, language_code, word):
        definitions = cls.fetch_by_language_and_word(language_code, word)
        definition_scores = \
                cls.fetch_definition_scores_by_language_and_word(language_code, word)
        kw_scores = \
                cls.fetch_keyword_score_dictionary_for_language_and_word(language_code, word)
        return definitions, definition_scores, kw_scores

    @classmethod
    def fetch_definition_scores_by_language_and_word(cls, language_code, word):
        return definition_votes.\
                DefinitionVote.sum_for_language_and_word(language_code, word)

    @classmethod
    def fetch_keyword_score_dictionary_for_language_and_word(cls, language_code, word):
        scores = cls.fetch_keyword_scores_by_language_and_word(language_code, word)
        return cls._build_keyword_score_dictionary(scores)

    @classmethod
    def fetch_keyword_scores_by_language_and_word(cls, language_code, word):
        return word_votes.\
                WordVote.sum_for_language_and_word(language_code, word)

    @classmethod
    def _build_keyword_score_dictionary(cls, keyword_scores):
        dictionary = defaultdict(lambda : cls._build_ordereddefaultdict(OrderedDict))
        for score in keyword_scores:
            dictionary[score.definitionid][score.place][score.natlangwordid] = score.score
        return dictionary

    @staticmethod
    def _build_ordereddefaultdict(factory):
        d = OrderedDefaultDict()
        d.default_factory = factory
        return d

    @classmethod
    def fetch_by_language_and_word(cls, language_code, word):
        query = cls.query.\
                by_language_tag_and_valsi_word(language_code, word).\
                fully_loaded_by_language_tag_and_valsi_word()
        return query.all()

    @classmethod
    def fetch_for_id_with_scores(cls, definition_id, language_code=None, word=None):
        definition = cls.fetch_for_id(definition_id, language_code=language_code, word=word)
        def_score = cls.fetch_score_for_definition_id(definition_id)
        kw_scores = cls.fetch_keyword_score_dictionary_for_definition_id(definition_id)
        return definition, def_score, kw_scores

    @classmethod
    def fetch_for_id(cls, definition_id, language_code=None, word=None):
        query= cls.query.\
                for_id(definition_id, language_code=language_code, word=word).\
                fully_loaded_by_language_tag_and_valsi_word()
        return query.first()

    @classmethod
    def fetch_score_for_definition_id(cls, definition_id):
        return definition_votes.\
                DefinitionVote.sum_for_definition_id(definition_id)

    @classmethod
    def fetch_keyword_score_dictionary_for_definition_id(cls, definition_id):
        scores = cls.fetch_keyword_scores_for_definition_id(definition_id)
        dictionary_by_definition_id = cls._build_keyword_score_dictionary(scores)
        return dictionary_by_definition_id.get(definition_id, {})

    @classmethod
    def fetch_keyword_scores_for_definition_id(cls, definition_id):
        return word_votes.\
                WordVote.sum_for_definition_id(definition_id)

    @classmethod
    def fetch_best_by_language_and_word(cls, language_code, word):
        query = cls.query.\
                best_by_language_tag_and_valsi_word(language_code, word)
        return query.first()

    @property
    def language_tag(self):
        return self.language.tag if self.language else None

    @property
    def word(self):
        return self.valsi.word if self.valsi else None

    @property
    def updated_at(self):
        return None if self.time == 0 else datetime.fromtimestamp(self.time)

    def keywords(self):
        keyword_scores = self.annotation("keyword_scores")
        if keyword_scores:
            return self._build_sorted_keyword_dictionary(keyword_scores)
        else:
            return self._build_unsorted_keyword_dictionary()

    def _build_sorted_keyword_dictionary(self, keyword_scores):
        dictionary = self._build_ordered_list_dictionary()
        for mapping in self.keyword_mappings:
            self._apply_keyword_score_to_mapping(mapping, keyword_scores)
            dictionary[mapping.place].append(mapping)
        self._sort_keywords(dictionary)
        return dictionary

    @staticmethod
    def _build_ordered_list_dictionary():
        dictionary = OrderedDefaultDict()
        dictionary.default_factory = list
        return dictionary

    def _apply_keyword_score_to_mapping(self, mapping, keyword_scores):
        score = 0
        place_scores = keyword_scores.get(mapping.place, None)
        if place_scores:
            score = place_scores.get(mapping.natlangwordid, 0)
        mapping.annotate(score=score)

    def _sort_keywords(self, dictionary):
        for place, mappings in dictionary.iteritems():
            mappings.sort(key=lambda m: m.annotation("score", 0), reverse=True)

    def _build_unsorted_keyword_dictionary(self):
        dictionary = self._build_ordered_list_dictionary()
        for mapping in self.keyword_mappings:
            dictionary[mapping.place].append(mapping)
        return dictionary

    def __repr__(self):
        return '<Definition %d: "%s">' % \
                (self.definitionid, self.definition.encode("utf-8"))

