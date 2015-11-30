
from marshmallow import fields

from ..utils import uri_munge_lojban
from ..web.endpoints import Endpoint
from abstract import AbstractItemSchema, AbstractCollectionSchema
from custom_fields import DictionaryField, OrderedNested
import users, examples, languages, keyword_mappings, valsi

class ItemSchema(AbstractItemSchema):

    MODEL_FIELDS = [ "valsi", "selmaho", "language", "definition",
                     "jargon", "notes", "examples", "user", "updated_at" ]

    definition_id  = fields.Int()
    valsi          = fields.Nested(valsi.WordSchema, only="word")
    selmaho        = fields.Str()
    language       = fields.Nested(languages.ItemSchema, only="tag")
    definition     = fields.Str()
    gloss_words    = fields.List(fields.Nested(keyword_mappings.ItemSchema))
    place_keywords = DictionaryField(OrderedNested(keyword_mappings.ItemSchema))
    jargon         = fields.Str()
    notes          = fields.Str()
    examples       = fields.List(fields.Nested(examples.ItemSchema))
    user           = fields.Nested(users.ItemSchema, only="username", dump_only=True)
    score          = fields.Int(dump_only=True)
    updated_at     = fields.DateTime(dump_only=True)
    _links         = fields.Raw(dump_only=True)

    def _build_serialization_dictionary(self, model):
        data = {}
        data["definition_id"] = model.definitionid
        for field in self.MODEL_FIELDS:
            value = getattr(model, field, None)
            if value:
                data[field] = value
        self._add_keywords(model, data)
        self._add_optional_fields(model, data)
        data["_links"] = self._build_hal_links(model)
        examples = data.get("examples", None)
        if examples and (len(examples) == 0):
            del data["examples"]
        return data

    def _add_keywords(self, model, data):
        keywords = model.keywords()
        gloss_words = keywords.pop(0, [])
        if keywords:
            data["place_keywords"] = {k : v[0] for k, v in keywords.iteritems()}
        if gloss_words:
            data["gloss_words"] = gloss_words

    def _add_optional_fields(self, model, data):
        score = model.annotation("score")
        if score is not None:
            data["score"] = score

    def _endpoint(self):
        return Endpoint.for_name("DefinitionsItem")

    def _view_arguments(self, model):
        return {
            "word"          : uri_munge_lojban(model.word),
            "language_code" : model.language_tag,
            "definition_id" : model.definitionid
        }

class CollectionSchema(AbstractCollectionSchema):

    items      = fields.List(OrderedNested(ItemSchema))
    updated_at = fields.DateTime(dump_only=True)
    _links     = fields.Raw(dump_only=True)

    def _endpoint(self):
        return Endpoint.for_name("DefinitionsCollection")

