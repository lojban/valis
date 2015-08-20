
# valis: valis, a lojbanic information system
# Copyright (C) 2015, Riley Martinez-Lynch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask.ext.restful import Api
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from flask import make_response, jsonify

from ..context import app
import endpoints

DEFAULT_PORT = 5000

api  = Api(app, prefix="/data")

def configure():
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(configured_web_port(), site)

def configured_web_port():
    server_name = configured_server_name()
    if server_name:
        server_name_components = server_name.split(":")
        if len(server_name_components) > 1:
            return int(server_name_components[1])
    return DEFAULT_PORT

def configured_server_name():
    return app.config.get('SERVER_NAME')

def add_resources_to_api(resources):

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

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'srera': 'fliba lo ka facki'}), 404)

