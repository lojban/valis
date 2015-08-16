
from flask import request
from marshmallow import fields

from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema, AbstractCollectionSchema

class ItemSchema(AbstractItemSchema):

    username     = fields.Str()
    name         = fields.Str()
    _links       = fields.Raw(dump_only=True)

    def _build_serialization_dictionary(self, model):
        return {
            "username" : model.username,
            "name"     : model.realname,
            "_links"   : self._build_hal_links(model)
        }

    def _endpoint(self):
        return Endpoint.for_name("UsersItem")

    def _view_arguments(self, model):
        return { "username" : model.username }

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
        return Endpoint.for_name("UsersCollection")

    def _options_for_next_url(self, collection):
        options = request.args.copy()
        last_item = collection.items[-1]
        last_user = last_item.username
        options["after"] = last_user
        return options

