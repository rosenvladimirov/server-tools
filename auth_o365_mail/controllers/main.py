# -*- coding: utf-8 -*-
import time

import werkzeug
import werkzeug.utils

# import odoo
# from O365.utils import EnvTokenBackend

from odoo import http, tools, _
from odoo.http import request
# from odoo.addons.web.controllers.main import ensure_db
# from odoo.tools.config import config
# from odoo.exceptions import AccessError, AccessDenied, UserError
from odoo.addons.auth_o365_mail.models.auth_oauth import AUTHORITY, SCOPES
# from odoo.addons.web.controllers.main import Home
# import json

import logging

from odoo.tools import config

_logger = logging.getLogger(__name__)


class WebsiteO365(http.Controller):

    @http.route('/o365/login', type='http', auth="user", website=True)
    def o365_login(self, redirect=None, **kw):
        values = request.params.copy()
        _logger.info("VALUES login %s" % values)
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)

        o365_provider = request.env.ref('auth_o365_mail.provider_o365_o365')

        if request.httprequest.method == 'POST':
            scope = values['scopes']
            scopes = SCOPES[scope]
            if values['scopes'] != 'basic':
                scopes.append('offline_access')
                scopes.append('User.Read')
            _logger.info("VALUES scopes %s" % scopes)

            o365_account, url, state = o365_provider._get_provider_authorization_url(scopes=scopes)

            response = werkzeug.utils.redirect(url, 303)
            # values.update({
            #     # 'website': request.website,
            #     'tenant_id': o365_account.con.tenant_id,
            #     # 'user': o365_account.get_current_user(),
            #     'main_resource': o365_account.main_resource,
            #     'access_token': o365_account.con.token_backend.get_token(),
            #     'disable_footer': False,
            #     'disable_database_manager': True,
            # })
            # request.session['o365_user'] = o365_account.main_resource
            # response = request.render('auth_o365_mail.status', values)

        elif request.httprequest.method == 'GET':
            values.update({
                # 'website': request.website,
                'client_id': o365_provider.client_id,
                'tenant_id': o365_provider.tenant_id,
                'disable_footer': False,
                'disable_database_manager': True,
            })
            response = request.render('auth_o365_mail.login', values)
        elif redirect is not None:
            response = werkzeug.utils.redirect(redirect, 303)
        else:
            response = http.local_redirect('/web', query=request.params, keep_hash=True)
        return response

    @http.route('/o365/logout', type='http', auth="user", website=True)
    def o365_logout(self):
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        if config.get('proxy_mode', False) and not base_url.startswith('https://') and base_url.find('http://') != -1:
            base_url = 'https://' + base_url.split('http://')[1]
        request.session.clear()  # Wipe out user and its token cache from session
        return werkzeug.utils.redirect(AUTHORITY + "/oauth2/v2.0/logout" + "?" + werkzeug.url_encode({
            'post_logout_redirect_uri': base_url,
        }))

    @http.route('/o365', type='http', auth="public", website=True)
    def o365(self, **kw):
        values = request.params.copy()
        _logger.info("VALUES /o365 %s" % values)

        if not request.session.uid:
            params = {
                'redirect': '/0365/login'
            }
            return werkzeug.utils.redirect('/web/login?' + werkzeug.url_encode(params), 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        o365_provider = request.env.ref('auth_o365_mail.provider_o365_o365')
        request_url = request.httprequest and request.httprequest.url or ''
        if config.get('proxy_mode', False) and not request_url.startswith('https://') and request_url.find('http://') != -1:
            request_url = 'https://' + request_url.split('http://')[1]

        _logger.info("request.httpresponse.url: %s:%s" % (request.httprequest and request.httprequest.url or 'None', request_url))

        result, o365_account = o365_provider._get_provider_request_token(request_url)
        _logger.info("RESULT %s:%s" % (result, o365_account))
        if not result:
            return http.local_redirect('/web', query=request.params, keep_hash=True)
        values.update({
            # 'website': request.website,
            'tenant_id': o365_account.con.tenant_id,
            'main_resource': o365_account.main_resource(),
            'access_token': result.get('access_token'),
            'disable_footer': False,
            'disable_database_manager': True,
        })
        return request.render('auth_o365_mail.status', values)
