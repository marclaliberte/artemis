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
from datetime import datetime
import logging
import gevent
import hpfeeds
import MySQLdb

from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger('artemis')


class FeedPuller(object):
    def __init__(self, config):

        self.mysqlserver = config['mysqlserver']
        self.mysqluser = config['mysqluser']
        self.mysqlpwd = config['mysqlpass']
        self.mysqldb = config['mysqldb']
        self.ident = config['hpf_ident']
        self.secret = config['hpf_secret']
        self.port = config['hpf_port']
        self.host = config['hpf_host']
        self.feeds = config['hpf_channels']
        self.last_received = datetime.now()

        self.hpc = None
        self.enabled = True
        self.db_cursor = None

    def db_connect(self):
        db_conn = MySQLdb.conect(host=self.mysqlserver,
                                 user=self.mysqluser,
                                 passwd=self.mysqlpwd,
                                 db=self.mysqldb)

        db_conn.autocommit(True)
        return db_conn

    def start_listening(self):

        gevent.spawn_later(15, self._activity_checker)
        while self.enabled:
            try:
                self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)

                def on_error(payload):
                    logger.error('Error message from broker: {0}'.format(payload))
                    self.hpc.stop()

                def on_message(ident, chan, payload):
                    self.last_received = datetime.now()
                    db_conn = self.db_connect()
                    db_cursor = db_conn.cursor()

                    handler = BaseHandler(ident,db_cursor)
                    handler.select_module(chan)
                    handler.handle_payload(payload)

                    db_conn.close()
                    

                self.hpc.subscribe(self.feeds)
                self.hpc.run(on_message, on_error)
            except Exception as ex:
                print ex
                self.hpc.stop()
                logger.exception('Exception caught: {0}'.format(ex))
            #throttle
            gevent.sleep(5)

    def stop(self):
        self.hpc.stop()
        self.enabled = False
        logger.info("FeedPuller stopped.")

    def _activity_checker(self):
        while self.enabled:
            if self.hpc is not None and self.hpc.connected:
                difference = datetime.now() - self.last_received
                if difference.seconds > 15:
                    logger.warning('No activity for 15 seconds, forcing reconnect')
                    self.hpc.stop()
            gevent.sleep(15)
