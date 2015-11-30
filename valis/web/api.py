
from flask.ext.restful import Api

from ..context import app

api = Api(app, prefix="/api")

def configure():
    from .. import resources

    # /valsi
    endpoint = resources.valsi.collection_endpoint
    api.add_resource(resources.valsi.Collection, endpoint.path_template,
                     endpoint=endpoint.name)

    # /valsi/WORD
    endpoint = resources.valsi.item_endpoint
    api.add_resource(resources.valsi.Item, endpoint.path_template,
                     endpoint=endpoint.name)

    # /valsi/WORD/LANGUAGE
    endpoint = resources.definitions.collection_endpoint
    api.add_resource(resources.definitions.Collection, endpoint.path_template,
                     endpoint=endpoint.name)

    # /valsi/WORD/LANGUAGE/ID
    endpoint = resources.definitions.item_endpoint
    api.add_resource(resources.definitions.Item, endpoint.path_template,
                     endpoint=endpoint.name)

    # /languages
    endpoint = resources.languages.collection_endpoint
    api.add_resource(resources.languages.Collection, endpoint.path_template,
                     endpoint=endpoint.name)

    # /languages/LANGUAGE
    endpoint = resources.languages.item_endpoint
    api.add_resource(resources.languages.Item, endpoint.path_template,
                     endpoint=endpoint.name)

    # /languages/LANGUAGE/words
    endpoint = resources.words.collection_by_language_endpoint
    api.add_resource(resources.words.CollectionByLanguage, endpoint.path_template,
                     endpoint=endpoint.name)

    # /languages/LANGUAGE/words/WORD
    endpoint = resources.words.collection_endpoint
    api.add_resource(resources.words.Collection, endpoint.path_template,
                     endpoint=endpoint.name)

    # /languages/LANGUAGE/words/WORD/ID
    endpoint = resources.words.item_endpoint
    api.add_resource(resources.words.Item, endpoint.path_template,
                     endpoint=endpoint.name)

    # /users/USER
    endpoint = resources.users.item_endpoint
    api.add_resource(resources.users.Item, endpoint.path_template,
                     endpoint=endpoint.name)

