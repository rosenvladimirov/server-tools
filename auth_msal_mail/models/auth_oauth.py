# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models
import base64
import msal

_logger = logging.getLogger(__name__)

AUTHORITY = 'https://login.microsoftonline.com/'


class AuthOAuthProvider(models.Model):
    """Class defining the configuration values of an OAuth2 provider"""

    _inherit = 'auth.oauth.provider'

    tenant_id = fields.Char('Directory (tenant) ID')
    client_secret = fields.Char('Client secrets')
    token_cache = None

    def _get_provider(self, cache=None, authority=None):
        if authority is None:
            authority = AUTHORITY + self.tenant_id
        app = msal.ConfidentialClientApplication(self.client_id,
                                                 authority=authority,
                                                 client_credential=self.client_secret,
                                                 token_cache=cache)
        return app

    def _get_from_provider_accounts(self, scope, cache=None, authority=None):
        if not scope:
            scope = self.scope
        cca = self._get_provider(cache=cache, authority=authority)
        accounts = cca.get_accounts()
        if accounts:  # So all account(s) belong to the current signed-in user
            result = cca.acquire_token_silent(scope, account=accounts[0])
            return result
        return False

    def _build_auth_code_flow(self, authority=None, scopes=None):
        return self._get_provider(authority=authority).\
            initiate_auth_code_flow(scopes or [], redirect_uri=url_for("authorized", _external=True))

    def get_access_token(self, app=False, scope=False):
        result = {}
        if not app:
            app = self._get_provider()
        if scope:
            result = app.acquire_token_for_client(scopes=scope)
            _logger.info("Get token result %s" % result)
        return result.get('access_token')

    def generate_auth_string(self, app, scope, user):
        token = self.get_access_token(app, scope=scope)
        if not token:
            return None
        xoauth = f"user={user}\1auth=Bearer {token}\1\1"
        # xoauth = xoauth.encode('ascii')
        # xoauth = base64.b64encode(xoauth)
        return xoauth
