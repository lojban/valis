
from marshmallow import fields

from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema
import users

class ItemSchema(AbstractItemSchema):

    content  = fields.Str()
    user     = fields.Nested(users.ItemSchema, only="username", dump_only=True)

    def _build_serialization_dictionary(self, model):
        return {
            "content"  : model.content,
            "user"     : model.user
        }

