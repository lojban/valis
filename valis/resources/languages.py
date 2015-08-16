
from flask import abort
from marshmallow import Schema, fields

from ..web.endpoints import Endpoint
from ..schema.languages import CollectionSchema, ItemSchema
from ..models import Language
from abstract import AbstractCollectionResource, AbstractItemResource

class CollectionOptionsSchema(Schema):
    code_prefix = fields.Str()
    after_code  = fields.Str()
    limit       = fields.Int()

collection_endpoint = Endpoint("LanguagesCollection",
                                "/languages",
                                options_schema=CollectionOptionsSchema())

collection_schema = CollectionSchema()

class Collection(AbstractCollectionResource):

    def get(self):
        options = self._parse_options()
        models, count = self._fetch_filtered_with_count(**options)
        collection = self._build_collection(models, count)
        return self._serialize_collection(collection)

    def _fetch_filtered_with_count(self, limit=None, **kwargs):
        limit = self._bind_limit(limit)
        models, count = Language.fetch_filtered_with_count(limit=limit, **kwargs)
        if not models:
            abort(404)
        return models, count

    def _endpoint(self):
        return collection_endpoint

    def _schema(self):
        return collection_schema

item_endpoint = \
        Endpoint("LanguagesItem",
                "/languages/<string:code>")

item_schema = ItemSchema()

class Item(AbstractItemResource):

    def get(self, code):
        model = self._fetch_model(code)
        return self._serialize_model(model)

    def _fetch_model(self, code):
        model = Language.fetch_for_tag(code)
        if not model:
            abort(404)
        return model

    def _schema(self):
        return item_schema

