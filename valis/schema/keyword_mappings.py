
from marshmallow import fields

from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema
import languages, users

class ItemSchema(AbstractItemSchema):

    word       = fields.Str()
    sense      = fields.Str()
    language   = fields.Nested(languages.ItemSchema, only="tag")
    user       = fields.Nested(users.ItemSchema, only="username", dump_only=True)
    score      = fields.Int(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    _links     = fields.Raw()

    def _build_serialization_dictionary(self, model):
        word = model.word
        data = {
            "word"       : word.word,
            "language"   : word.language,
            "sense"      : word.meaning,
            "user"       : word.user,
            "updated_at" : word.updated_at,
            "_links"     : self._build_hal_links(model)
        }
        self._add_optional_fields(model, data)
        if not word.meaning:
            del data["sense"]
        return data

    def _add_optional_fields(self, model, data):
        score = model.annotation("score")
        if score is not None:
            data["score"] = score

    def _endpoint(self):
        return Endpoint.for_name("WordsItem")

    def _view_arguments(self, model):
        word = model.word
        return {
            "language_code" : word.language_tag,
            "word"          : word.word,
            "word_id"       : word.wordid
        }

