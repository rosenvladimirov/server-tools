# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import psycopg2

from odoo import api, fields, models, _, Command
from odoo.addons.base.models.ir_module import Module
from odoo.tools import sql

_logger = logging.getLogger(__name__)
_schema = logging.getLogger('odoo.schema')


class IrModuleModule(models.Model):
    _name = "ir.module.module"
    _description = 'Module'
    _inherit = _name

    indexes_ids = fields.One2many('ir.module.module.indexes', compute='_compute_indexes_ids', string='Module indexes')

    @staticmethod
    def _get_methods(method, where):
        if method == 'btree' and where.find('IS NOT NULL') != -1:
            method = 'btree_not_null'
        elif method == 'brin' and where.find('IS NOT NULL') == -1:
            method = 'brin_not_null'
        elif method:
            method = 'index'
        elif not method or method is None:
            method = 'None'
        return method

    def _get_fields(self):
        res = []
        for line in self.env['ir.model.fields'].sudo().search([]).filtered(lambda r: r.modules.find(self.name) != -1):
            res.append(f"field_{line.model.replace('.', '_')}__{line.name}")
        return res

    def _get_indexes(self):
        res = []
        for line in self.env['ir.model'].sudo().search([]).filtered(lambda r: r.modules.find(self.name) != -1):
            res.append(line.model)
        return res

    def _get_xml_id(self, field_name):
        field_name = f"field_{field_name.model_name.replace('.', '_')}__{field_name.name}"
        domain = [('model', '=', 'ir.model.fields'), ('name', '=', field_name)]
        res = self.env['ir.model.data'].sudo().search_read(domain, ['module', 'name', 'res_id'], limit=1)
        return res[0]['res_id']

    def _compute_indexes_ids(self):
        for record in self:
            trust_fields = self._get_fields()
            indexes = self.pool._check_indexes(self._cr, record._get_indexes(), info=True, value_fields=trust_fields)
            record.indexes_ids = False
            if indexes:
                for index_name, table_name, expression, method, where, field in indexes:
                    # _logger.info(f"index data {index_data}")
                    record.indexes_ids |= record.indexes_ids.create({
                        'module_id': record.id,
                        'index_name': index_name,
                        'table_name': table_name,
                        'expression': expression,
                        'methods': self._get_methods(method, where),
                        'where': where,
                        'field_model': self._get_xml_id(field),
                    })

    def button_reindex(self):
        for record in self:
            trust_fields = record._get_fields()
            existing_models = record._get_indexes()
            _logger.info(f'Existing models: {existing_models}')
            self.pool.re_index(self._cr, existing_models, value_fields=trust_fields)


class ModuleIndexes(models.TransientModel):
    _name = "ir.module.module.indexes"
    # _table = "ir_module_module_indexes"
    _description = "Module indexes"
    # _auto = False

    module_id = fields.Many2one('ir.module.module', string='Module', index=True, ondelete='cascade')
    index_name = fields.Char('Index name')
    table_name = fields.Char('Table name')
    expression = fields.Char('Expression')
    methods = fields.Selection([
        ('btree', _('B-TREE')),
        ('btree_not_null', _('B-TREE without null value')),
        ('brin', 'Brin'),
        ('brin_not_null', _('BRIN with null value')),
        ('trigram', _('Trigram')),
        ('index', _('Indexed')),
        ('None', _('Non indexed')),
    ], string='Methods')
    where = fields.Char('Where condition')
    field_model = fields.Many2one('ir.model.fields', string='Fields', ondelete='cascade')
