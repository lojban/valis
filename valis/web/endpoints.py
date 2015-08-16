
from flask import request, url_for

class Endpoint(object):

    registry = {}

    @classmethod
    def register(cls, endpoint):
        cls.registry[endpoint.name] = endpoint

    @classmethod
    def for_request(cls):
        return cls.for_name(request.endpoint)

    @classmethod
    def for_name(cls, name):
        return cls.registry[name]

    def __init__(self, name, path_template, options_schema=None):
        self.name                 = name
        self.path_template        = path_template
        self.options_schema       = options_schema
        self.register(self)

    def parse_options(self, input_options=None):
        if self.options_schema:
            if input_options is None:
                input_options = request.args
            options, _ = self.options_schema.load(input_options)
        else:
            options = {}
        return options

    def build_url(self, args=None, options=None):
        args = self._make_endpoint_args(None, args, options)
        return url_for(self.name, _external=True, **args)

    def build_url_for_request(self, args=None, options=None):
        args = self._make_endpoint_args(request, args, options)
        return url_for(self.name, _external=True, **args)

    def _make_endpoint_args(self, request, view_args, options):
        args = {}
        if view_args is None:
            view_args = request.view_args if request else {}
        if options is None:
            options = request.args if request else {}
        options = self.parse_options(options)
        args.update(options)
        args.update(view_args)
        return args

