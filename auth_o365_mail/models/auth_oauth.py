# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os

from odoo import fields, models, tools, _
from odoo.tools import config
import base64
import O365

# from O365 import Account, MSGraphProtocol, MSOffice365Protocol, FileSystemTokenBackend

_logger = logging.getLogger(__name__)

AUTHORITY = 'https://login.microsoftonline.com/'
SCOPES = {
    'basic': ['offline_access', 'User.Read'],
    'mailbox': ['Mail.Read'],
    'mailbox_shared': ['Mail.Read.Shared'],
    'message_send': ['Mail.Send'],
    'message_send_shared': ['Mail.Send.Shared'],
    'message_all': ['Mail.ReadWrite', 'Mail.Send'],
    'message_all_shared': ['Mail.ReadWrite.Shared', 'Mail.Send.Shared'],
    'address_book': ['Contacts.Read'],
    'address_book_shared': ['Contacts.Read.Shared'],
    'address_book_all': ['Contacts.ReadWrite'],
    'address_book_all_shared': ['Contacts.ReadWrite.Shared'],
    'calendar': ['Calendars.Read'],
    'calendar_shared': ['Calendars.Read.Shared'],
    'calendar_all': ['Calendars.ReadWrite'],
    'calendar_shared_all': ['Calendars.ReadWrite.Shared'],
    'tasks': ['Tasks.Read'],
    'tasks_all': ['Tasks.ReadWrite'],
    'users': ['User.ReadBasic.All'],
    'onedrive': ['Files.Read.All'],
    'onedrive_all': ['Files.ReadWrite.All'],
    'sharepoint': ['Sites.Read.All'],
    'sharepoint_dl': ['Sites.ReadWrite.All'],
}


class AuthOAuthProvider(models.Model):
    """Class defining the configuration values of an OAuth2 provider"""

    _inherit = 'auth.oauth.provider'

    tenant_id = fields.Char('Directory (tenant) ID')
    client_secret = fields.Char('Client secrets')
    o365_auth_flow_type = fields.Selection([
        ('authorization', _('On behalf of a user')),
        ('public', _('On behalf of a user (public)')),
        ('credentials', _('With your own identity '))
    ], string='Authentication')
    o365_state = fields.Char('O365 State')
    o365_account = None

    def generate_auth_string(self, token, user):
        if not token:
            return False
        auth_string = f"user={user}%x01auth=Bearer {token}%x01%x01"
        return base64.b64encode(auth_string.encode('ascii'))

    def _get_provider(self, user=None, password=None, auth_flow_type=None, protocol=None, scopes=None, token=None):
        token_path = tools.config.filestore(self.env.cr.dbname)

        if protocol is None:
            protocol = O365.MSGraphProtocol()
        token_backend = O365.FileSystemTokenBackend(token_path=os.path.join(token_path, 'private'),
                                                    token_filename='odoo_o365_token.txt')
        if token is not None and token in ("authenticate", "load"):
            token_backend.token = token_backend.load_token() if token == "load" else None
        credentials = (self.client_id, self.client_secret)
        kwargs = {
            "tenant_id": self.tenant_id,
            'protocol': protocol,
            'token_backend': token_backend,
        }
        if auth_flow_type is not None:
            kwargs.update({
                'auth_flow_type': auth_flow_type,
            })
        if user is not None or (auth_flow_type is not None and auth_flow_type in ("credentials", "password")):
            kwargs.update({
                "tenant_id": self.tenant_id,
            })
        if user is not None:
            kwargs.update({
                "scopes": scopes is None and SCOPES["basic"] or scopes,
                'username': user,
                'password': password,
            })
        o365_account = O365.Account(credentials, **kwargs)

        if o365_account and scopes and not o365_account.is_authenticated:
            o365_account, url, state = self._get_provider_authorization_url(o365_account=o365_account, scopes=scopes)
        else:
            return o365_account

        if o365_account.is_authenticated:
            if not o365_account.con.refresh_token():
                raise UserWarning(_('Error when refresh token'))

        _logger.info("Access to O365 %s => %s(%s) and token %s" %
                     (protocol, o365_account,
                      o365_account and o365_account.main_resource or '',
                      token_backend and o365_account.con.token_backend.get_token() or ''))

        # _logger.info("Token from MSAL %s(%s)" % (self.token_backend, self.token_backend.token))
        self.o365_account = o365_account
        self.o365_auth_flow_type = kwargs.get('auth_flow_type', '')
        return o365_account

    def _get_provider_token(self, user, password=None, scopes=None):
        o365_account = self._get_provider(user=user, password=password, scopes=scopes, token='load')
        return o365_account.con.token_backend.get_token()

    def _get_provider_authorization_url(self, o365_account=False, scopes=False):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if config.get('proxy_mode', False) and not base_url.startswith('https://') and base_url.find('http://') != -1:
            base_url = 'https://' + base_url.split('http://')[1]

        callback = base_url + "/o365"
        if self.scope:
            scopes = self.scope.split(',')
            scopes = list(map(lambda r: r.strip(), scopes))
        scopes = scopes or SCOPES["basic"]
        if not o365_account:
            o365_account = self._get_provider()
        url, state = o365_account.con.get_authorization_url(requested_scopes=scopes, redirect_uri=callback)
        _logger.info("SCOPES %s:%s %s" % (scopes, state, url))
        self.o365_state = state
        # self.o365_account = o365_account
        return o365_account, url, state

    def _get_provider_request_token(self, url):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if config.get('proxy_mode', False) and not base_url.startswith('https://') and base_url.find('http://') != -1:
            base_url = 'https://' + base_url.split('http://')[1]
        callback = base_url + "/o365"
        result = False
        o365_account = self._get_provider()
        if not o365_account.is_authenticated:
            # if self.scope:
            #     scopes = self.scope.split(',')
            #     scopes = list(map(lambda r: r.strip(), scopes))
            # scopes = scopes or SCOPES["basic"]
            result = o365_account.con.request_token(url,
                                                    state=self.o365_state,
                                                    redirect_uri=callback,
                                                    store_token=True)
            _logger.info("RESULT %s" % result)
            # if o365_account.con.refresh_token():
            #     return result, o365_account

            # url, o365_state = o365_account.con.get_authorization_url(requested_scopes=scopes, redirect_uri=callback)
            # self.o365_state = o365_state
            # self.o365_account = o365_account
        # else:
        #     result = o365_account.con.request_token(AUTHORITY, state=self.o365_state, redirect_uri=callback, store_token=True)
        return result, o365_account
