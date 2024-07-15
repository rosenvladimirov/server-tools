# -*- coding: utf-8 -*-
import time

import msal
import odoo

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db
from odoo.tools.config import config

from odoo.addons.web.controllers.main import Home
import json

import logging

_logger = logging.getLogger(__name__)


class WebsiteMsal(http.Controller):

    def _load_cache(self):
        o365_cache = msal.SerializableTokenCache()
        if request.session.get("o365_token_cache"):
            o365_cache.deserialize(request.session["o365_token_cache"])
        return o365_cache

    def _save_cache(self, o365_cache):
        if o365_cache.has_state_changed:
            request.session["o365_token_cache"] = o365_cache.serialize()

    def _get_token_from_cache(self, scope=None):
        result = {}
        o365_cache = self._load_cache()  # This web app maintains one cache per session
        auth_id = request.env.ref('auth_msal_mail.provider_o365')
        if auth_id:
            result = auth_id._get_from_provider_accounts(cache=o365_cache, scope=scope)
        return result

    @http.route('/o365/login', type='http', auth="none", sitemap=False)
    def o365_login(self, redirect=None, **kw):
        ensure_db()
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if values['databases'] is not None \
                and (values['database'].get(config.get('db_name')) or values['databases'][0]):
            response = request.render('auth_oauth.login', values)
        else:
            response = http.local_redirect('/web', query=request.params, keep_hash=True)
        return response

    @http.route('/o365/logout', type='http', auth="none", sitemap=False)
    def o365_logout(self):
        request.session.clear()  # Wipe out user and its token cache from session
        return redirect(
            app_config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("index", _external=True))

    @http.route(['/o365'], type='http', auth="public", website=True)
    def o365(self, **kw):
        if not request.session.get('o365_user') or not request.session.uid:
            return request.redirect("/o365/login")
        if not request.session.uid:
            kw.update({'redirect': '/o365/login'})
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)
