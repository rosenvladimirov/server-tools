# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL

from odoo import api, models, _
from odoo.addons.fetchmail.models.fetchmail import FetchmailServer as fetchmailserver

_logger = logging.getLogger(__name__)
MAIL_TIMEOUT = 60


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    def _imap_login(self, connection):
        """Authenticate the IMAP connection.
        Can be overridden in other module for different authentication methods.
        :param connection: The IMAP connection to authenticate
        """
        self.ensure_one()
        connection.login(self.user, self.password)

    @api.multi
    def connect(self):
        self.ensure_one()
        if self.type == 'imap':
            if self.is_ssl:
                connection = IMAP4_SSL(self.server, int(self.port))
            else:
                connection = IMAP4(self.server, int(self.port))
            self._imap_login(connection)
        elif self.type == 'pop':
            if self.is_ssl:
                connection = POP3_SSL(self.server, int(self.port))
            else:
                connection = POP3(self.server, int(self.port))
            #TODO: use this to remove only unread messages
            #connection.user("recent:"+server.user)
            connection.user(self.user)
            connection.pass_(self.password)
        # Add timeout on socket
        connection.sock.settimeout(MAIL_TIMEOUT)
        return connection

fetchmailserver.connect = FetchmailServer.connect
