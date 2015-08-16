
from collections import defaultdict, OrderedDict

class OrderedDefaultDict(OrderedDict, defaultdict):
    pass

class DomainCache(object):

    def __init__(self):
        self.values = {}

    def reload_values(self):
        self.values = self.load_values()

    def load_values(self):
        raise NotImplementedError

    def __getitem__(self, value):
        if value not in self.values:
            self.reload_values()
        return self.values[value]

def uri_munge_lojban(lojban):
    return lojban.replace("'", "h")

def uri_unmunge_lojban(lojban):
    return lojban.replace("h", "'")

