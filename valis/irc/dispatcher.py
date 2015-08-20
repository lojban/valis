
# pylint: disable=I0011, C0111, no-self-use

import re

from twisted.python import log

class BaseDispatcher(object):

    def __init__(self, client):
        self.client = client
        self._filtered_nickname = None
        self._filter_expression = None

    def dispatch_private_message(self, user_nickname, response_channel, message):
        log.msg('<%(user_nickname)s> %(message)s' % locals())
        command = self.parse_private_message(message)
        if command:
            self.dispatch_command(user_nickname, response_channel, command)

    def parse_private_message(self, message):
        return self.parse_command(message)

    def parse_command(self, message):
        """By default, pass message as is"""
        return message

    def dispatch_public_message(self, user_nickname, response_channel, message):
        command = self.parse_public_message(message)
        if command:
            log.msg('<%(user_nickname)s> %(message)s' % locals())
            self.dispatch_command(user_nickname, response_channel, command)

    def parse_public_message(self, message):
        filtered = self.filter_public_message(message)
        return self.parse_command(filtered) if filtered else None

    def filter_public_message(self, message):
        match = re.match(self._get_filter_expression(), message)
        return match.group('query') if match else None

    def _get_filter_expression(self):
        expression = None
        if hasattr(self, '_filtered_nickname'):
            if self._filtered_nickname == self.client.nickname:
                expression = self._filter_expression
        return expression or self._reset_filter_expression()

    def _reset_filter_expression(self):
        self._filtered_nickname = self.client.nickname
        self._filter_expression = \
            r'^%(nickname)s[:,]?\s*(?P<query>.+)' \
            % dict(nickname=re.escape(self._filtered_nickname))
        return self._filter_expression

    def dispatch_command(self, nick, response_channel, command):
        """Template method to be overridden"""
        pass

