
# pylint: disable=I0011, C0111, too-few-public-methods

class Mixin(object):
    """Mixin for IRC protocols with factories that provide a nick"""

    @property
    def nickname(self):
        return self.factory.nickname

    @nickname.setter
    def nickname(self, _):
        """Ignoring assignments"""
        pass

