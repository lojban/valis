
from flask.ext.sqlalchemy import BaseQuery

from ..context import db

class Query(BaseQuery):

    def filtered(self, username_prefix=None, after_username=None):
        query = self
        if username_prefix:
            query = query.filter(User.username.startswith(username_prefix))
        if after_username:
            query = query.filter(User.username > after_username)
        return query

    def ordered_by_username(self):
        return self.order_by(User.username)

    def limited(self, limit=None):
        return self.limit(limit) if limit else self

    def for_username(self, username):
        return self.filter(User.username == username)

class User(db.Model):

    query_class = Query

    __table__ = db.Model.metadata.tables["users"]

    @classmethod
    def fetch_filtered_with_count(cls, limit=None, **kwargs):
        models = cls.fetch_filtered(limit=limit, **kwargs)
        count = cls.count_filtered(**kwargs)
        return models, count

    @classmethod
    def fetch_filtered(cls, limit=None, **kwargs):
        query = cls.query.\
                filtered(**kwargs).\
                ordered_by_username().\
                limited(limit=limit)
        return query.all()

    @classmethod
    def count_filtered(cls, **kwargs):
        query = cls.query.\
                filtered(**kwargs)
        return query.count()

    @classmethod
    def fetch_for_username(cls, username):
        query = cls.query.\
                for_username(username)
        return query.first()

    def __repr__(self):
        return '<User "%s">' % self.username.encode("utf-8")

