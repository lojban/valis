
# pylint: disable=I0011, C0111, bare-except, too-many-ancestors

import re

from .dispatcher import BaseDispatcher
from .factory_naming import Mixin as FactoryNamingMixin
from .protocol import DispatchableIrcClient

from ..models import Definition, Language
from ..utils import tex2text

class Dispatcher(BaseDispatcher, object):

    RULES            = ["affix", "class", "type", "notes", "definition"]
    DEFAULT_RULE     = "definition"
    DEFAULT_LANGUAGE = "en"

    def __init__(self, client):
        super(Dispatcher, self).__init__(client)

    def dispatch_command(self, nick, target, query):
        response = self._response_for_query(query)
        if response:
            self._msg(target, response)

    def _response_for_query(self, query):
        language, rule, text = self._parse_query(query)
        if text:
            definition = self._fetch_best_definition(language, text)
            if definition:
                return self._response_for_rule_and_definition(rule, definition)

    def _response_for_rule_and_definition(self, rule, definition):
        if rule == 'definition':
            return tex2text(definition.definition)
        elif rule == 'class':
            return definition.selmaho
        elif rule == 'type':
            return definition.valsi.type
        elif rule == 'notes':
            return tex2text(definition.notes)

    def _parse_query(self, query):
        lang = rule = None
        match = re.search(r'^\s*(.*?)\s*(?:\((?:([^):]+):)?([^)]+)\))?\s*$', query)
        if match:
            text, lang, rule_or_lang = \
                    match.group(1), match.group(2), match.group(3)
            if lang:
                lang = self._parse_language_tag(lang)
            if rule_or_lang:
                rule = self._parse_rule(rule_or_lang)
                if (not lang) and (not rule):
                    lang = self._parse_language_tag(rule_or_lang)
        lang = lang or self.DEFAULT_LANGUAGE
        rule = rule or self.DEFAULT_RULE
        return lang, rule, text

    @staticmethod
    def _parse_language_tag(text):
        text = text.lower()
        if Language.fetch_for_tag(text):
            return text

    def _parse_rule(self, text):
        text = text.lower()
        if text in self.RULES:
            return text

    @staticmethod
    def _fetch_best_definition(language_code, word):
        return Definition.fetch_best_by_language_and_word(language_code, word)

    def _msg(self, target, text):
        self.client.msg(target, text)

class Protocol(FactoryNamingMixin, DispatchableIrcClient):

    def _initialize_dispatcher(self):
        self.dispatcher = Dispatcher(self)

