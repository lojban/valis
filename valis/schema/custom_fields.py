
from marshmallow import fields
from marshmallow.base import FieldABC

class DictionaryField(fields.Field):

    def __init__(self, cls_or_instance, **kwargs):
        super(DictionaryField, self).__init__(**kwargs)
        if isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, FieldABC):
                raise ValueError('The type of the dictionary value elements '
                                           'must be a subclass of '
                                           'marshmallow.base.FieldABC')
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, FieldABC):
                raise ValueError('The instances of the dictionary value '
                                           'elements must be of type '
                                           'marshmallow.base.FieldABC')
            self.container = cls_or_instance

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        elif isinstance(value, dict):
            return { k: self.container._serialize(v, attr, obj) for k, v in value.iteritems() }
        else:
            raise TypeError

# Nested fields ordinarily use the "ordered" value of their parents
class OrderedNested(fields.Nested):

    @property
    def schema(self):
        schema = super(OrderedNested, self).schema
        schema.ordered = True
        return schema


