
from flask import request
from marshmallow import fields

from ..utils import uri_munge_lojban
from ..web.endpoints import Endpoint
from custom_fields import DictionaryField, OrderedNested
from abstract import AbstractItemSchema, AbstractCollectionSchema, OrderedSchema
import users, languages, valsi

class EmbeddedDefinitionSchema(AbstractItemSchema):

    word   = fields.Nested(valsi.WordSchema, only="word")
    _links = fields.Raw()

    def _build_serialization_dictionary(self, model):
        data = { "word" : model.valsi }
        data["_links"] = self._build_hal_links(model)
        return data

    def _endpoint(self):
        return Endpoint.for_name("DefinitionsItem")

    def _view_arguments(self, model):
        return {
            "word"          : uri_munge_lojban(model.word),
            "language_code" : model.language_tag,
            "definition_id" : model.definitionid
        }

class EmbeddedDefinitionsSchema(OrderedSchema):

    as_gloss_word    = fields.List(fields.Nested(EmbeddedDefinitionSchema))
    as_place_keyword = DictionaryField(fields.List(OrderedNested(EmbeddedDefinitionSchema)))

class ItemSchema(AbstractItemSchema):

    word                  = fields.Str()
    sense                 = fields.Str()
    language              = fields.Nested(languages.ItemSchema, only="tag")
    user                  = fields.Nested(users.ItemSchema, only="username", dump_only=True)
    definition_references = fields.Nested(EmbeddedDefinitionsSchema)
    updated_at            = fields.DateTime(dump_only=True)
    _links                = fields.Raw()

    def _build_serialization_dictionary(self, model):
        data = {
            "word"       : model.word,
            "language"   : model.language,
            "sense"      : model.meaning,
            "user"       : model.user,
            "updated_at" : model.updated_at,
            "_links"     : self._build_hal_links(model)
        }
        self._add_definition_references(model, data)
        if not model.meaning:
            del data["sense"]
        return data

    def _add_definition_references(self, model, data):
        definitions = {}
        keywords = model.keywords()
        glosswords = keywords.pop(0, [])
        if glosswords:
            definitions["as_gloss_word"] = glosswords
        if keywords:
            definitions["as_place_keyword"] = keywords
        if definitions:
            data["definition_references"] = definitions

    def _endpoint(self):
        return Endpoint.for_name("WordsItem")

    def _view_arguments(self, model):
        return {
            "language_code" : model.language_tag,
            "word"          : model.word,
            "word_id"       : model.wordid
        }

class CollectionSchema(AbstractCollectionSchema):

    items      = fields.List(fields.Nested(ItemSchema))
    count      = fields.Int(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    _links     = fields.Raw(dump_only=True)

    def _endpoint(self):
        return Endpoint.for_name("WordsCollection")

    def _options_for_next_url(self, collection):
        options = request.args.copy()
        last_item = collection.items[-1]
        last_word = last_item.word
        options["after_word"] = last_word
        return options

class CollectionByLanguageSchema(CollectionSchema):

    def _endpoint(self):
        return Endpoint.for_name("WordsByLanguageCollection")

