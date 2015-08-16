
from flask import request
from marshmallow import fields

from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema, AbstractCollectionSchema

class ItemSchema(AbstractItemSchema):

    MODEL_FIELDS = [ "tag", "realname", "englishname", "lojbanname" ]

    code         = fields.Str(attribute="tag")
    name         = fields.Str(attribute="realname")
    english_name = fields.Str(attribute="englishname")
    lojban_name  = fields.Str(attribute="lojbanname")
    _links       = fields.Raw(dump_only=True)

    def _build_serialization_dictionary(self, model):
        data = {}
        for field in self.MODEL_FIELDS:
            value = getattr(model, field, None)
            if value:
                data[field] = value
        data["_links"] = self._build_hal_links(model)
        return data

    def _endpoint(self):
        return Endpoint.for_name("LanguagesItem")

    def _view_arguments(self, model):
        return { "code" : model.tag }

class CollectionSchema(AbstractCollectionSchema):

    items      = fields.List(fields.Nested(ItemSchema))
    count      = fields.Int(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    _links     = fields.Raw(dump_only=True)

    def _build_serialization_dictionary(self, collection):
        data = {
            "items"      : collection.items,
            "count"      : collection.count,
            "updated_at" : collection.updated_at,
            "_links"     : self._build_hal_links(collection)
        }
        return data

    def _endpoint(self):
        return Endpoint.for_name("LanguagesCollection")

    def _options_for_next_url(self, collection):
        options = request.args.copy()
        last_item = collection.items[-1]
        last_code = last_item.tag
        options["after_code"] = last_code
        return options

