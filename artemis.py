
# Copyright (C) 2017 Marc Laliberte <marc@marclab.net>
#
# This code is based on mnemosyne (https://github.com/johnnykv/mnemosyne)
# by Johnny Vastergaard, copyright 2012.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#!/usr/bin/env python
import feedpuller
from datetime import datetime
from ConfigParser import ConfigParser
import os
import sys
import hpfeeds
import gevent
import json
import logging
import MySQLdb

from daemon import runner


logger = logging.getLogger('artemis')

class Artemis(object):
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/opt/artemis/logs/artemis_out.log'
        self.stderr_path = '/opt/artemis/logs/artemis_err.log'
        self.pidfile_path = '/opt/artemis/pid/artemis.pid'
        self.pidfile_timeout = 5
        self.logfile = '/opt/artemis/logs/artemis.log'
        self.config_file = '/opt/artemis/config.cfg'

    def parse_config(self,config_file):
        if not os.path.isfile(config_file):
            logger.critical("Could not find configuration file: {0}".format(config_file))
            sys.exit("Could not find configuration file: {0}".format(config_file))

        parser = ConfigParser()
        parser.read(config_file)

        config = {}

        config['mysqldb'] = parser.get('mysql', 'database')
        config['mysqluser'] = parser.get('mysql', 'user')
        config['mysqlpass'] = parser.get('mysql', 'password')

        config['hpf_channels'] = parser.get('hpfeeds', 'channels')
        config['hpf_ident'] = parser.get('hpfeeds', 'ident')
        config['hpf_secret'] = parser.get('hpfeeds', 'secret')
        config['hpf_port'] = parser.getint('hpfeeds', 'port')
        config['hpf_host'] = parser.get('hpfeeds', 'host')

        return config


    def run(self):
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            filename=self.logfile,
                            level=logging.DEBUG)

        try:
            while True:
                logger.info("Artemis Storage Server starting up...")
                c = self.parse_config(self.config_file)

                db_conn = MySQLdb.connect(host="localhost",
                                     user=c['mysqluser'],
                                     passwd=c['mysqlpass'],
                                     db=c['mysqldb'])

                db_conn.autocommit(True)
                db_cursor = db_conn.cursor()


                greenlets = {}

                puller = feedpuller.FeedPuller(db_cursor, c['hpf_ident'], c['hpf_secret'], c['hpf_port'], c['hpf_host'], c['hpf_channels'])
                greenlets['hpfeeds-puller'] = gevent.spawn(puller.start_listening)

                try:
                    gevent.joinall(greenlets.values())
                except KeyboardInterrupt as err:
                    if puller:
                        puller.stop()
                        db_conn.close()

                gevent.joinall(greenlets.values())
        except (SystemExit,KeyboardInterrupt):
            pass
        except:
            logger.exception("Exception")
        finally:
            logger.info("Artemis Storage Server shutting down...")


#def parse_config(config_file):
#    if not os.path.isfile(config_file):
#        logger.critical("Could not find configuration file: {0}".format(config_file))
#        sys.exit("Could not find configuration file: {0}".format(config_file))

#    parser = ConfigParser()
#    parser.read(config_file)

#    config = {}

#    config['mysqldb'] = parser.get('mysql', 'database')
#    config['mysqluser'] = parser.get('mysql', 'user')
#    config['mysqlpass'] = parser.get('mysql', 'password')

#    config['hpf_channels'] = parser.get('hpfeeds', 'channels')
#    config['hpf_ident'] = parser.get('hpfeeds', 'ident')
#    config['hpf_secret'] = parser.get('hpfeeds', 'secret')
#    config['hpf_port'] = parser.getint('hpfeeds', 'port')
#    config['hpf_host'] = parser.get('hpfeeds', 'host')

#    return config

if __name__ == '__main__':
    daemon_runner = runner.DaemonRunner(Artemis())
    daemon_runner.daemon_context.detach_process=True
    daemon_runner.do_action()

#    logfile = 'logs/artemis.log'
#    config_file = 'config.cfg'
#    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#                        filename=logfile,
#                        level=logging.DEBUG)

#    c = parse_config(config_file)

#    db_conn = MySQLdb.connect(host="localhost",
#                         user=c['mysqluser'],
#                         passwd=c['mysqlpass'],
#                         db=c['mysqldb'])

#    db_conn.autocommit(True)
#    db_cursor = db_conn.cursor()

#    logger.info('Starting Artemis Storage')

#    greenlets = {}

#    puller = feedpuller.FeedPuller(db_cursor, c['hpf_ident'], c['hpf_secret'], c['hpf_port'], c['hpf_host'], c['hpf_channels'])
#    greenlets['hpfeeds-puller'] = gevent.spawn(puller.start_listening)

#    try:
#        gevent.joinall(greenlets.values())
#    except KeyboardInterrupt as err:
#        if puller:
#            puller.stop()
#            db_conn.close()

#    gevent.joinall(greenlets.values())
