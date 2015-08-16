
from collections import namedtuple
from datetime import datetime

from flask import request
from flask.ext.restful import Resource

Collection = namedtuple("Collection", ["items", "count", "updated_at"])

class AbstractCollectionResource(Resource):

    COLLECTION_LIMIT_MAX     = 100
    COLLECTION_LIMIT_DEFAULT = 20

    def _parse_options(self):
        options, _ = self._endpoint().options_schema.load(request.args)
        return options

    def _endpoint(self):
        raise NotImplementedError

    def _bind_limit(self, limit):
        if limit and (limit > 0) and (limit <= self.COLLECTION_LIMIT_MAX):
            return limit
        else:
            return self.COLLECTION_LIMIT_DEFAULT

    def _build_collection(self, models, count=None):
        return Collection(models, count, datetime.utcnow())

    def _serialize_collection(self, collection):
        serialized, _ = self._schema().dump(collection)
        return serialized

    def _schema(self):
        raise NotImplementedError

class AbstractItemResource(Resource):

    def _serialize_model(self, model):
        serialized, _ = self._schema().dump(model)
        return serialized

    def _schema(self):
        raise NotImplementedError

