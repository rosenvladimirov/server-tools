# Copyright 2024 Rosen Vladimirov
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Module Reindex',
    'summary': """
        reindex module models""",
    'version': '17.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/server-tools/tree/17.0',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_views.xml',
    ],
    'demo': [
    ],
}
