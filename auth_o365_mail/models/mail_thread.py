# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, models, tools
from odoo.tools import decode_smtp_header, decode_message_header

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """ Update MailThread to add the support of bounce management in mass mailing statistics. """
    _inherit = 'mail.thread'

    # @api.model
    # def message_route_process(self, message, message_dict, routes):
    #     _logger.info("MESSAGE ROUTE \nROUTE: %s \n%s" % (routes, message))
    #     return super(MailThread, self).message_route_process(message, message_dict, routes)

    @api.model
    def message_process(self, model, message, custom_values=None, save_original=False, strip_attachments=False, thread_id=None):
        _logger.info("\nMODEL: %s \nthread_id: %s \ncustom_values: %s" % (model, thread_id, custom_values))
        return super(MailThread, self).\
            message_process(model, message,
                            custom_values=custom_values,
                            save_original=save_original,
                            strip_attachments=strip_attachments,
                            thread_id=thread_id)
