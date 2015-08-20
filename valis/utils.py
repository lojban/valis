# -*- coding: utf-8 -*-

import re

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

# the following routines were borrowed from vlasisku

def tex2text(tex):
    return strip_html(tex2html(tex))

def tex2html(tex):
    """Turn most of the TeX used in jbovlaste into HTML.

    >>> tex2html('$x_1$ is $10^2*2$ examples of $x_{2}$.')
    u'x<sub>1</sub> is 10<sup>2\\xd72</sup> examples of x<sub>2</sub>.'
    >>> tex2html('\emph{This} is emphasised and \\\\textbf{this} is boldfaced.')
    u'<em>This</em> is emphasised and <strong>this</strong> is boldfaced.'
    """
    def math(m):
        t = []
        for x in m.group(1).split('='):
            x = x.replace('{', '').replace('}', '')
            x = x.replace('*', u'×')
            if '_' in x:
                t.append(u'%s<sub>%s</sub>' % tuple(x.split('_')[0:2]))
            elif '^' in x:
                t.append(u'%s<sup>%s</sup>' % tuple(x.split('^')[0:2]))
            else:
                t.append(x)
        return '='.join(t)
    def typography(m):
        if m.group(1) == 'emph':
            return u'<em>%s</em>' % m.group(2)
        elif m.group(1) == 'textbf':
            return u'<strong>%s</strong>' % m.group(2)
    def lines(m):
        format = '\n%s'
        if m.group(1).startswith('|'):
            format = '\n<span style="font-family: monospace">    %s</span>'
        elif m.group(1).startswith('>'):
            format = '\n<span style="font-family: monospace">   %s</span>'
        return format % m.group(1)
    def puho(m):
        format = 'inchoative\n<span style="font-family: monospace">%s</span>'
        return format % m.group(1)
    tex = re.sub(r'\$(.+?)\$', math, tex)
    tex = re.sub(r'\\(emph|textbf)\{(.+?)\}', typography, tex)
    tex = re.sub(r'(?![|>\-])\s\s+(.+)', lines, tex)
    tex = re.sub(r'inchoative\s\s+(----.+)', puho, tex)
    return tex

def strip_html(text):
    """Strip HTML from a string.

    >>> strip_html('x<sub>1</sub> is a variable.')
    'x1 is a variable.'
    """
    return re.sub(r'<.*?>', '', text.replace('\n', '; '))

