
from datetime import datetime

from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy.orm import joinedload, subqueryload

from ..utils import OrderedDefaultDict
from ..context import db
import domains, valsi_types, users, etymologies, definitions

class Query(BaseQuery):

    def filtered(self, word_prefix=None, word_suffix=None, user=None, type=None, after_word=None):
        query = self
        if word_prefix:
            query = query.\
                    filter(Valsi.word.startswith(word_prefix))
        if word_suffix:
            query = query.\
                    filter(Valsi.word.endswith(word_suffix))
        if type:
            query = query.\
                    join(valsi_types.ValsiType).\
                    filter(valsi_types.ValsiType.descriptor == type)
        if user:
            query = query.\
                    join(users.User).\
                    filter(users.User.username == user)
        if after_word:
            query = query.\
                    filter(Valsi.word > after_word)
        return query

    def ordered_by_word(self):
        return self.order_by(Valsi.word)

    def limited(self, limit=None):
        return self.limit(limit) if limit else self

    def for_word(self, word):
        return self.filter(Valsi.word == word)

    def fully_loaded(self):
        return self.\
                options(joinedload(Valsi.user),
                        subqueryload(Valsi.etymologies).\
                                joinedload(etymologies.Etymology.language,
                                           etymologies.Etymology.user),
                        subqueryload(Valsi.definitions).\
                                joinedload(definitions.Definition.language))

class Valsi(db.Model):

    query_class = Query
    __table__ = db.Model.metadata.tables["valsi"]

    user  = db.relationship(users.User,
                            backref=db.backref("valsi", lazy="dynamic"))

    @classmethod
    def fetch_filtered_with_count(cls, limit=None, **kwargs):
        models = cls.fetch_filtered(limit=limit, **kwargs)
        count = cls.count_filtered(**kwargs)
        return models, count

    @classmethod
    def fetch_filtered(cls, limit=None, **kwargs):
        query = cls.query.\
                filtered(**kwargs).\
                ordered_by_word().\
                fully_loaded().\
                limited(limit=limit)
        return query.all()

    @classmethod
    def count_filtered(cls, **kwargs):
        query = cls.query.\
                filtered(**kwargs)
        return query.count()

    @classmethod
    def fetch_for_word(cls, word):
        query = cls.query.\
                for_word(word=word).\
                fully_loaded()
        return query.first()

    @property
    def type(self):
        return domains.VALSI_TYPES[self.typeid]

    @property
    def updated_at(self):
        return None if self.time == 0 else datetime.fromtimestamp(self.time)

    def affixes(self):
        return [] if self.rafsi is None else self.rafsi.split()

    def etymologies_by_language(self):
        return self._build_etymology_dictionary(self.etymologies)

    @staticmethod
    def _build_etymology_dictionary(etymologies):
        d = OrderedDefaultDict()
        d.default_factory = list
        for etymology in etymologies:
            d[etymology.language_tag].append(etymology)
        return d

    def __repr__(self):
        return '<Valsi %d: "%s">' % (self.valsiid, self.word.encode("utf-8"))

