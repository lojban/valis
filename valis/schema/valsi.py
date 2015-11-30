
from collections import defaultdict, OrderedDict

from flask import request
from marshmallow import Schema, fields

from ..utils import uri_munge_lojban
from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema, AbstractCollectionSchema
from custom_fields import DictionaryField, OrderedNested
import users, etymologies

class DefinitionLinkSchema(AbstractItemSchema):

    self = fields.Str()

    def _build_serialization_dictionary(self, model):
        return { "self" : self._build_self_url(model) }

    def _endpoint(self):
        return Endpoint.for_name("DefinitionsCollection")

    def _view_arguments(self, model):
        return {
            "word"          : uri_munge_lojban(model.word),
            "language_code" : model.language_tag
        }

class ItemSchema(AbstractItemSchema):

    word        = fields.Str()
    type        = fields.Str()
    rafsi       = fields.List(fields.Str())
    etymologies = DictionaryField(fields.List(OrderedNested(etymologies.ItemSchema)))
    definitions = DictionaryField(fields.Nested(DefinitionLinkSchema, only="self"), dump_only=True)
    user        = fields.Nested(users.ItemSchema, only="username", dump_only=True)
    updated_at  = fields.DateTime(dump_only=True)
    _links      = fields.Raw(dump_only=True)

    def _build_serialization_dictionary(self, model):
        rafsi = model.affixes()
        etymologies = model.etymologies_by_language()
        data = {
            "word"        : model.word,
            "type"        : model.type,
            "rafsi"       : rafsi,
            "user"        : model.user,
            "etymologies" : etymologies,
            "definitions" : self._prototype_definition_by_language_tag(model),
            "updated_at"  : model.updated_at,
            "_links"      : self._build_hal_links(model)
        }
        if len(rafsi) == 0:
            del data["rafsi"] # don't display empty rafsi
        if len(etymologies) == 0:
            del data["etymologies"]
        return data

    def _prototype_definition_by_language_tag(self, model):
        """Return only one definition (the 'prototype') per language"""
        definitions_by_tag = OrderedDict()
        definitions = self._definitions_by_language_tag(model)
        for tag in sorted(definitions.keys()):
            definitions_by_tag[tag] = definitions[tag][0]
        return definitions_by_tag

    def _definitions_by_language_tag(self, model):
        definitions_by_tag = defaultdict(list)
        for d in model.definitions:
            definitions_by_tag[d.language_tag].append(d)
        return definitions_by_tag

    def _endpoint(self):
        return Endpoint.for_name("ValsiItem")

    def _view_arguments(self, model):
        return { "word" : uri_munge_lojban(model.word) }

class CollectionSchema(AbstractCollectionSchema):

    items      = fields.List(OrderedNested(ItemSchema))
    count      = fields.Int(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    _links     = fields.Raw(dump_only=True)

    def _endpoint(self):
        return Endpoint.for_name("ValsiCollection")

    def _options_for_next_url(self, collection):
        options = request.args.copy()
        last_item = collection.items[-1]
        last_word = last_item.word
        options["after_word"] = uri_munge_lojban(last_word)
        return options

class WordSchema(Schema):
    word = fields.Str()

