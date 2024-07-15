.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Logger on syslog server
=======================

This addon possibility to send log data to log server. This is interesting for setups server address on syslog server and port.

New config keys for default:

``logserver=tcp://localhost:514``


Installation
============

To install this module, you only need to add it to your addons, and load it as
a server-wide module.

This can be done with the ``server_wide_modules`` parameter in ``/etc/odoo.conf``
or with the ``--load`` command-line parameter

``server_wide_modules = "web, logger_server"``

Configuration
=============

And make sure that add the key's in Odoo's configuration file:

``logserver=[[tcp:// or udp://]][[syslog server ip address]]:[[optional syslog server port, default is 514]]``

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/rosenvladimirov/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Rosen Vladimirov <vladimirov.rosen@gmail.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
