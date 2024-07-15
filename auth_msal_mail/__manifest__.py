# Copyright 2022 Rosen Vladimirov, bioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Auth Msal Mail',
    'summary': """
        Add msal authenticate for imap and smtp servers.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov, bioPrint Ltd.,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/server-tools',
    'depends': [
        'mail_fix_connection_login',
        'auth_oauth',
        'web',
    ],
    'data': [
        'data/auth_oauth_data.xml',
        'views/auth_oauth_views.xml',
        'views/fetchmail_views.xml',
    ],
    'demo': [
    ],
}
