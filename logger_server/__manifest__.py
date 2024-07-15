# © 2021  Rosen Vladimirov <vladimirov.rosen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Logger on log server",
    "summary": "Added confuguration for logging on log server localhost:514",
    "version": "11.0.1.0.0",
    "author": "Rosen Vladimirov, "
              "BioPrint Ltd."
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "complexity": "normal",
    "category": "Tools",
    "depends": [
        'web',
    ],
    "data": [
    ],
    "js": [
    ],
    "css": [
    ],
    "auto_install": False,
    'installable': True,
    "external_dependencies": {
        'python': [
            'jaraco.docker'
        ],
    },
}
