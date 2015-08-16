
from sqlalchemy.ext.declarative import AbstractConcreteBase

class Annotated(AbstractConcreteBase):

    def annotate(self, **kwargs):
        annotations = getattr(self, "_annotations", None)
        if not annotations:
            annotations = self._annotations = {}
        annotations.update(kwargs)

    def annotation(self, key, default=None):
        annotations = getattr(self, "_annotations", None)
        if annotations:
            return annotations.get(key, default)
        else:
            return default

