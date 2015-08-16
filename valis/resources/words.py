
from flask import abort
from marshmallow import Schema, fields

from ..web.endpoints import Endpoint
from ..models import Word
from ..schema.words import ItemSchema, CollectionSchema, CollectionByLanguageSchema
from abstract import AbstractCollectionResource, AbstractItemResource

class CollectionByLanguageOptionsSchema(Schema):
    word_prefix = fields.Str()
    word_suffix = fields.Str()
    after_word  = fields.Str()
    limit       = fields.Int()

collection_by_language_endpoint = \
        Endpoint("WordsByLanguageCollection",
                "/languages/<string:language_code>/words",
                options_schema=CollectionByLanguageOptionsSchema())

collection_by_language_schema = CollectionByLanguageSchema()

class CollectionByLanguage(AbstractCollectionResource):

    def get(self, language_code):
        options = self._parse_options()
        models, count = self._fetch_models_with_count(language_code=language_code, **options)
        collection = self._build_collection(models, count)
        return self._serialize_collection(collection)

    def _fetch_models_with_count(self, limit=None, **kwargs):
        limit = self._bind_limit(limit)
        models, count = Word.fetch_words_and_count(limit=limit, **kwargs)
        if not models:
            abort(404)
        return models, count

    def _endpoint(self):
        return collection_by_language_endpoint

    def _schema(self):
        return collection_by_language_schema

class CollectionOptionsSchema(Schema):
    limit = fields.Int()

collection_endpoint = \
        Endpoint("WordsCollection",
                "/languages/<string:language_code>/words/<string:word>",
                options_schema=CollectionOptionsSchema())

collection_schema = CollectionSchema()

class Collection(AbstractCollectionResource):

    def get(self, language_code, word):
        options = self._parse_options()
        models, count = self._fetch_models_with_count(language_code=language_code, word=word, **options)
        collection = self._build_collection(models, count)
        return self._serialize_collection(collection)

    def _endpoint(self):
        return collection_endpoint

    def _fetch_models_with_count(self, limit=None, **kwargs):
        limit = self._bind_limit(limit)
        models, count = Word.fetch_words_and_count(limit=limit, **kwargs)
        if not models:
            abort(404)
        return models, count

    def _schema(self):
        return collection_schema

item_endpoint = \
        Endpoint("WordsItem",
                "/languages/<string:language_code>/words/<string:word>/<int:word_id>")

item_schema = ItemSchema()

class Item(AbstractItemResource):

    def get(self, language_code, word, word_id):
        model = self._fetch_word(language_code, word, word_id)
        return self._serialize_model(model)

    def _fetch_word(self, language_code, word, word_id):
        model = Word.fetch_word(language_code, word, word_id)
        if not model:
            abort(404)
        return model

    def _schema(self):
        return item_schema

