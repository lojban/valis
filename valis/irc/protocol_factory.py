
# pylint: disable=I0011, C0111, R0903

from twisted.internet.protocol import ReconnectingClientFactory

class IrcClientFactory(ReconnectingClientFactory, object):

    def __init__(self, protocol, options):
        self.protocol = protocol
        self.nickname = options["name"]
        self.channels = options["channels"]

