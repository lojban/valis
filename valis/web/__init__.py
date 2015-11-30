
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

from flask import jsonify
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site

from ..context import app

DEFAULT_PORT = 5000

def configure():
    configure_api()
    configure_assets()
    configure_html()
    configure_reactor()

def configure_api():
    from . import api
    api.configure()

def configure_assets():
    from . import assets
    assets.configure()

def configure_html():
    from . import html
    html.configure()

def configure_reactor():
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(_configured_web_port(), site)

def _configured_web_port():
    server_name = _configured_server_name()
    if server_name:
        server_name_components = server_name.split(":")
        if len(server_name_components) > 1:
            return int(server_name_components[1])
    return DEFAULT_PORT

def _configured_server_name():
    return app.config.get('SERVER_NAME')

