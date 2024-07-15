# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import email
import logging

from odoo import api, models, fields, _
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)

MAIL_TIMEOUT = 60
SCOPES = ['basic', 'message_all']


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider')
    tenant_id = fields.Char('Directory (tenant) ID', related='oauth_provider_id.tenant_id')
    client_id = fields.Char('Client ID', related='oauth_provider_id.client_id')
    client_secret = fields.Char('Client secrets', related='oauth_provider_id.client_secret')
    type = fields.Selection(selection_add=[
        ('o365', _('MS Office 365'))
    ])

    def _imap_login(self, connection):
        if self.type == 'imap':
            if not self.oauth_provider_id or self.oauth_provider_id != self.env.ref('auth_o365_mail.provider_o365_o365'):
                UserWarning(_('Something is wrong. Incorrect provider.'))
                return
            try:
                token, resource = self.oauth_provider_id._get_provider_token(self.user, self.password, scopes=SCOPES)
                connection.authenticate("XOAUTH2", lambda x: token)
            except Exception:
                _logger.info("General failure when trying to fetch mail server %s for user %s", self.name, self.name,
                             exc_info=True)


    @api.multi
    def connect(self):
        self.ensure_one()
        if self.type == 'o365':
            return self.oauth_provider_id._get_provider(self.user, self.password, scopes=['basic', 'message_all'])
        return super(FetchmailServer, self).connect()

    @api.model
    def _fetch_o365_mails(self):
        """ Method called by cron to fetch mails from servers """
        return self.search([('state', '=', 'done'), ('type', '=', 'o365')]).fetch_mail()

    @api.multi
    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            if self.type == 'o365':
                # IrMailServer = self.env['ir.mail_server']
                additionnal_context['fetchmail_server_id'] = server.id
                additionnal_context['server_type'] = server.type
                count, failed = 0, 0
                res_id = None
                o365_account = self.oauth_provider_id._get_provider(user=self.user, password=self.password, scopes=SCOPES)
                mailbox = o365_account.mailbox()
                # inbox = mailbox.inbox_folder()
                query = mailbox.new_query().on_attribute('isRead').equals(False)
                # _logger.info("%s:%s" % (inbox.get_folders(), query))
                for msg in mailbox.get_messages(query=query):
                #     _logger.info("MESSAGE \n%s\n%s" %
                #                  (msg.subject, server.original))
                    try:
                        data = msg.get_mime_content().decode('utf-8')
                        # data = pycompat.to_native(data)
                        # data = email.message_from_string(data)
                        # _logger.info("MESSAGE BEFORE %s" % data)

                        res_id = MailThread.with_context(**additionnal_context).\
                            message_process(server.object_id.model, data,
                                            save_original=server.original, strip_attachments=(not server.attach))
                        msg.mark_as_read()
                        if not server.original:
                            msg.delete()
                    except Exception:
                        _logger.info('Failed to process mail from %s server %s.', server.type, server.name, exc_info=True)
                        failed += 1
                    if res_id and server.action_id:
                        server.action_id.with_context({
                            'active_id': res_id,
                            'active_ids': [res_id],
                            'active_model': self.env.context.get("thread_model", server.object_id.model)
                        }).run()
                    self._cr.commit()
                    count += 1
                _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type,
                             server.name, (count - failed), failed)
                server.write({'date': fields.Datetime.now()})
                return True
        return super(FetchmailServer, self).fetch_mail()
