
# pylint: disable=I0011, C0111, bad-whitespace

from twisted.internet import reactor

from . import protocol_factory
from .dispatch import Protocol

DEFAULT_HOST     = "irc.freenode.net"
DEFAULT_PORT     = 6667
DEFAULT_CHANNELS = ["#lojban"]
DEFAULT_NICKNAME = "lojbo"

DEFAULT_OPTIONS = {
    "host"     : DEFAULT_HOST,
    "port"     : DEFAULT_PORT,
    "channels" : DEFAULT_CHANNELS,
    "name"     : DEFAULT_NICKNAME
}

def configure(options=None):
    options = options or DEFAULT_OPTIONS
    factory = protocol_factory.IrcClientFactory(Protocol, options)
    reactor.connectTCP(options["host"], options["port"], factory)

def run(options=None):
    configure(options)
    reactor.run()

