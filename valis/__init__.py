
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

# pylint: disable=I0011, C0111, import-error, bad-whitespace, no-member

__version__ = '0.1.0'

import sys

from twisted.python import log
from twisted.internet import reactor

from . import context, web

def configure(config):
    context.configure(config)

def run():
    configure_irc_bot()
    configure_web()
    reactor.run()

def configure_irc_bot():
    from . import irc
    log.startLogging(sys.stdout)
    irc.configure()

def configure_web():
    install_web_resources()
    web.configure()

def install_web_resources():
    from . import resources, web
    web.add_resources_to_api(resources)

