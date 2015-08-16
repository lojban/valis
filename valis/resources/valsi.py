
from flask import abort
from marshmallow import Schema, fields

from ..web.endpoints import Endpoint
from ..utils import uri_unmunge_lojban, uri_munge_lojban
from ..schema.valsi import CollectionSchema, ItemSchema
from ..models import Valsi
from abstract import AbstractCollectionResource, AbstractItemResource

class CollectionOptionsSchema(Schema):
    type        = fields.Function(lambda x: uri_munge_lojban(x), attribute="type")
    user        = fields.Str()
    word_prefix = fields.Function(lambda x: uri_unmunge_lojban(x))
    word_suffix = fields.Function(lambda x: uri_unmunge_lojban(x))
    after_word  = fields.Function(lambda x: uri_unmunge_lojban(x))
    limit       = fields.Int()

collection_endpoint = Endpoint("ValsiCollection",
                                "/valsi",
                                options_schema=CollectionOptionsSchema())

collection_schema = CollectionSchema()

class Collection(AbstractCollectionResource):

    def get(self):
        options = self._parse_options()
        models, count = self._fetch_models_and_count(**options)
        collection = self._build_collection(models, count)
        return self._serialize_collection(collection)

    def _fetch_models_and_count(self, limit=None, **kwargs):
        limit = self._bind_limit(limit)
        models, count = Valsi.fetch_filtered_with_count(limit=limit, **kwargs)
        if not models:
            abort(404)
        return models, count

    def _endpoint(self):
        return collection_endpoint

    def _schema(self):
        return collection_schema

item_endpoint = \
        Endpoint("ValsiItem",
                "/valsi/<string:word>")

item_schema = ItemSchema()

class Item(AbstractItemResource):

    def get(self, word):
        word = uri_unmunge_lojban(word)
        model = self._fetch_model(word)
        return self._serialize_model(model)

    def _fetch_model(self, word):
        model = Valsi.fetch_for_word(word)
        if not model:
            abort(404)
        return model

    def _endpoint(self):
        return item_endpoint

    def _schema(self):
        return item_schema

