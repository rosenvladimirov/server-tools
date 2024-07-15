# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.http import request
from ipaddress import IPv4Network

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    only_local_net = fields.Boolean('Only local')

    @api.model
    def search_count(self, args):
        if len(args) == 2 and args[0][2] == 'share' and args[1][2] == 'login_date':
            args += [('only_local_net', '=', False)]
            _logger.info("USER Checking %s" % args)
        return super().search_count(args)

    @classmethod
    def _login(cls, db, login, password):
        if not password:
            return False
        name = user_id = False
        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.environ:
            ip = request.httprequest.environ["HTTP_X_FORWARDED_FOR"]
        else:
            ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'

        try:
            with cls.pool.cursor() as cr:
                # passwd = []
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                if login == '' and IPv4Network(ip).is_private:
                    for x in self.search([('id', '!=', SUPERUSER_ID)]):
                        valid_pass, replacement = x._crypt_context().verify_and_update(password, x.password_crypt)
                        if valid_pass:
                            user = x
                            break
                else:
                    user = self.search([('login', '=', login)])

                if user.only_local_net and IPv4Network(ip).is_global:
                    user = False

                if user:
                    name = user.name
                    user_id = user.id
                    user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()
        except odoo.exceptions.AccessDenied:
            user_id = False

        status = "successful" if user_id else "failed"
        if user_id:
            _logger.info("Login %s for db:%s login:%s from %s(%s) (user %s)", status, db, login, ip,
                         IPv4Network(ip).is_private, name or '')
        else:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
        return user_id
