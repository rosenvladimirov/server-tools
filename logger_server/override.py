# © 2021  Rosen Vladimirov <vladimirov.rosen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import logging.handlers
import os
import platform
import socket

import sys
from jaraco.docker import is_docker

from odoo import netsvc
from odoo import tools
from odoo import release
from odoo.netsvc import PostgreSQLHandler, PSEUDOCONFIG_MAPPER, DEFAULT_LOG_CONFIGURATION, ColoredFormatter, DBFormatter

_logger = logging.getLogger(__name__)


_logger_init = False
def init_logger():
    global _logger_init
    if _logger_init:
        return
    _logger_init = True

    logging.addLevelName(25, "INFO")
    logging.captureWarnings(True)

    from odoo.tools.translate import resetlocale
    resetlocale()

    # create a format for log messages and dates
    format = '%(asctime)s %(pid)s %(levelname)s %(dbname)s %(name)s: %(message)s'
    # Normal Handler on stderr
    handler = logging.StreamHandler()

    if tools.config['syslog']:
        # SysLog Handler
        syslog = '/dev/log'
        server = False
        socktype = False
        proto = False
        if tools.config['logserver']:
            address = tools.config['logserver'].split('//')
            if len(address) > 1:
                proto, address = address
            port = address.split(':')
            if len(port) > 1:
                address, port = port
            else:
                port = logging.SYSLOG_UDP_PORT

            if proto == 'udp:':
                socktype = socket.SOCK_DGRAM
            else:
                socktype = socket.SOCK_STREAM
            server = (address, port)
        else:
            if platform.system() == 'Darwin':
                syslog = '/var/run/log'
            if is_docker():
                syslog = '/dev/stderr'
        if os.name == 'nt':
            handler = logging.handlers.NTEventLogHandler("%s %s" % (release.description, release.version))
        else:
            if server:
                handler = logging.handlers.SysLogHandler(address=server, socktype=socktype)
            else:
                handler = logging.handlers.SysLogHandler(syslog)
        format = '%s %s' % (release.description, release.version) \
                + ':%(dbname)s:%(levelname)s:%(name)s:%(message)s'

    elif tools.config['logfile']:
        # LogFile Handler
        logf = tools.config['logfile']
        try:
            # We check we have the right location for the log files
            dirname = os.path.dirname(logf)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            if tools.config['logrotate'] is not False:
                if tools.config['workers'] and tools.config['workers'] > 1:
                    # TODO: fallback to regular file logging in master for safe(r) defaults?
                    #
                    # Doing so here would be a good idea but also might break
                    # situations were people do log-shipping of rotated data?
                    _logger.warn("WARNING: built-in log rotation is not reliable in multi-worker scenarios and may incur significant data loss. "
                                 "It is strongly recommended to use an external log rotation utility or use system loggers (--syslog) instead.")
                handler = logging.handlers.TimedRotatingFileHandler(filename=logf, when='D', interval=1, backupCount=30)
            elif os.name == 'posix':
                handler = logging.handlers.WatchedFileHandler(logf)
            else:
                handler = logging.FileHandler(logf)
        except Exception:
            sys.stderr.write("ERROR: couldn't create the logfile directory. Logging to the standard output.\n")

    # Check that handler.stream has a fileno() method: when running OpenERP
    # behind Apache with mod_wsgi, handler.stream will have type mod_wsgi.Log,
    # which has no fileno() method. (mod_wsgi.Log is what is being bound to
    # sys.stderr when the logging.StreamHandler is being constructed above.)
    def is_a_tty(stream):
        return hasattr(stream, 'fileno') and os.isatty(stream.fileno())

    if os.name == 'posix' and isinstance(handler, logging.StreamHandler) and is_a_tty(handler.stream):
        formatter = ColoredFormatter(format)
    else:
        formatter = DBFormatter(format)
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)

    if tools.config['log_db']:
        db_levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        postgresqlHandler = PostgreSQLHandler()
        postgresqlHandler.setLevel(int(db_levels.get(tools.config['log_db_level'], tools.config['log_db_level'])))
        logging.getLogger().addHandler(postgresqlHandler)

    # Configure loggers levels
    pseudo_config = PSEUDOCONFIG_MAPPER.get(tools.config['log_level'], [])

    logconfig = tools.config['log_handler']

    logging_configurations = DEFAULT_LOG_CONFIGURATION + pseudo_config + logconfig
    for logconfig_item in logging_configurations:
        loggername, level = logconfig_item.split(':')
        level = getattr(logging, level, logging.INFO)
        logger = logging.getLogger(loggername)
        logger.setLevel(level)

    for logconfig_item in logging_configurations:
        _logger.debug('logger level set: "%s"', logconfig_item)

netsvc.init_logger = init_logger
