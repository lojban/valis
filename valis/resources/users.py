
from flask import abort

from ..web.endpoints import Endpoint
from ..schema.users import ItemSchema
from ..models import User
from abstract import AbstractItemResource

item_endpoint = \
        Endpoint("UsersItem",
                "/users/<string:username>")

item_schema = ItemSchema()

class Item(AbstractItemResource):

    def get(self, username):
        model = self._fetch_user(username)
        if not model:
            abort(404)
        return self._serialize_model(model)

    def _fetch_user(self, username):
        return User.fetch_for_username(username)

    def _schema(self):
        return item_schema

