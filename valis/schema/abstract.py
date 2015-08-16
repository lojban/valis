
from marshmallow import Schema
from marshmallow.decorators import pre_dump

class OrderedSchema(Schema):

    class Meta:
        ordered = True

class AbstractItemSchema(OrderedSchema):

    @pre_dump
    def _pre_serialize(self, model):
        return self._build_serialization_dictionary(model)

    def _build_serialization_dictionary(self, model):
        raise NotImplementedError

    def _build_hal_links(self, model):
        return { "self" : self._build_self_url(model) }

    def _build_self_url(self, model):
        endpoint = self._endpoint()
        view_args = self._view_arguments(model);
        return endpoint.build_url(args=view_args)

    def _endpoint(self):
        raise NotImplementedError

    def _view_arguments(self, model):
        raise NotImplementedError

class AbstractCollectionSchema(OrderedSchema):

    @pre_dump
    def _pre_serialize(self, collection):
        return self._build_serialization_dictionary(collection)

    def _build_serialization_dictionary(self, collection):
        data = {
            "items"      : collection.items,
            "count"      : collection.count,
            "updated_at" : collection.updated_at,
            "_links"     : self._build_hal_links(collection)
        }
        if collection.count is None:
            del data["count"]
        return data

    def _build_hal_links(self, collection):
        links = {}
        links["self"] = self._build_self_url(collection)
        count = collection.count
        if count and (count > len(collection.items)):
            links["next"] = self._build_next_url(collection)
        return links

    def _build_self_url(self, collection):
        endpoint = self._endpoint()
        return endpoint.build_url_for_request()

    def _endpoint(self):
        raise NotImplementedError

    def _build_next_url(self, collection):
        endpoint = self._endpoint()
        options = self._options_for_next_url(collection)
        return endpoint.build_url_for_request(options=options)

    def _options_for_next_url(self, collection):
        raise NotImplementedError

