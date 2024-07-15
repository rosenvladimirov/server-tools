# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json
import werkzeug.urls
import werkzeug.utils

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as oauthlogin
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request
from odoo import api, http, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class OAuthLogin(Home):

    def _get_auth_endpoint(self, auth_endpoint):
        return auth_endpoint

    def _get_return_url(self):
        return request.httprequest.url_root + 'auth_oauth/signin'

    def _get_auth_params(self, provider, return_url, state):
        return dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )

    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            auth_endpoint = self._get_auth_endpoint(provider['auth_endpoint'])
            return_url = self._get_return_url()
            state = self.get_state(provider)
            params = self._get_auth_params(provider, return_url, state)
            provider['auth_link'] = "%s?%s" % (auth_endpoint, werkzeug.url_encode(params))
        return providers

    def _get_error(self):
        error = request.params.get('oauth_error')
        if error == '1':
            error = _("Sign up is not allowed on this database.")
        elif error == '2':
            error = _("Access Denied")
        elif error == '3':
            error = _(
                "You do not have access to this database or your invitation has expired. Please ask for an invitation and be sure to follow the link in your invitation email.")
        else:
            error = None
        return error

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        providers = self.list_providers()

        response = super(OAuthLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = self._get_error()
            response.qcontext['providers'] = providers
            if error:
                response.qcontext['error'] = error

        return response


oauthlogin.list_providers = OAuthLogin.list_providers
oauthlogin.web_login = OAuthLogin.web_login
