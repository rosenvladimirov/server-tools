# Copyright 2022 Rosen Vladimirov, BioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Auth O365 Mail',
    'summary': """
        Add support for Office 365""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov, BioPrint Ltd.,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/server-tools',
    'conflicts': [
        'auth_msal_mail',
    ],
    'depends': [
        'auth_oauth',
        'fetchmail',
        'mail',
    ],
    'data': [
        'data/auth_oauth_data.xml',
        'views/auth_oauth_views.xml',
        'views/fetchmail_views.xml',
        'views/webclient_template.xml',
    ],
    'demo': [
    ],
}
