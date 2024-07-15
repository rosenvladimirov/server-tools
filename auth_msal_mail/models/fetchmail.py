# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging

from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)

MAIL_TIMEOUT = 60
SCOPE = ['https://outlook.office.com/.default']


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider')
    tenant_id = fields.Char('Directory (tenant) ID', related='oauth_provider_id.tenant_id')
    client_id = fields.Char('Client ID', related='oauth_provider_id.client_id')
    client_secret = fields.Char('Client secrets', related='oauth_provider_id.client_secret')

    @api.multi
    def _imap_login(self, connection):
        self.ensure_one()
        if not self.oauth_provider_id or self.oauth_provider_id != self.env.ref('auth_msal_mail.provider_o365'):
            UserWarning(_('Something is wrong. Incorrect provider.'))
            return
        try:
            connection.debug = 4
            connection.\
                authenticate("XOAUTH2", lambda x: base64.b64encode(self.oauth_provider_id.generate_auth_string(False, SCOPE, self.user).encode('utf-8')))
        except Exception:
            _logger.info("General failure when trying to fetch mail server %s for user %s", self.name, self.name,
                         exc_info=True)
