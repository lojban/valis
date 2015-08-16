
from flask.ext.sqlalchemy import BaseQuery

from ..context import db

class Query(BaseQuery):

    def filtered(self, code_prefix=None, after_code=None):
        query = self
        if code_prefix:
            query = query.filter(Language.tag.startswith(code_prefix))
        if after_code:
            query = query.filter(Language.tag > after_code)
        return query

    def ordered_by_tag(self):
        return self.order_by(Language.tag)

    def limited(self, limit=None):
        return self.limit(limit) if limit else self

    def for_tag(self, tag):
        return self.filter(Language.tag == tag)

class Language(db.Model):

    query_class = Query

    __table__ = db.Model.metadata.tables['languages']

    @classmethod
    def fetch_filtered_with_count(cls, limit=None, **kwargs):
        models = cls.fetch_filtered(limit=limit, **kwargs)
        count = cls.count_filtered(**kwargs)
        return models, count

    @classmethod
    def fetch_filtered(cls, limit=None, **kwargs):
        query = cls.query.\
                filtered(**kwargs).\
                ordered_by_tag().\
                limited(limit=limit)
        return query.all()

    @classmethod
    def count_filtered(cls, **kwargs):
        query = cls.query.\
                filtered(**kwargs)
        return query.count()

    @classmethod
    def fetch_for_tag(cls, tag):
        query = cls.query.\
                for_tag(tag)
        return query.first()

    def __repr__(self):
        return '<Language %s: "%s">' % \
                (self.language_tag, self.realname.encode('utf-8'))

