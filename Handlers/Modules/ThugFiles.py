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

import os
import sys
import logging
import MySQLdb as mdb
import base64
import json
import datetime

logger = logging.getLogger('artemis')

class ThugFiles(object):

    def __init__(self,db_cursor):
        self.db_cursor = db_cursor
        self.ident = None
        self.payload = None

    def save_file(self,payload):
        try:
            decoded = json.loads(str(payload))
            logger.debug('Decoded file payload')
        except:
            decoded = {'raw': payload}
            logger.debug('Saving file payload as raw data')

        if not 'md5' in decoded or not 'data' in decoded:
            logger.error('Received file does not contain hash or data - Ignoring it')
            return

        filedata = decoded['data'].decode('base64')
        path = "/var/artemis/files/thug/" + decoded['md5']
        logger.debug('Saving Thug file')
        fd = open(path, 'wb')
        fd.write(filedata)
        logger.debug('Thug file saved')

        now = datetime.datetime.now()
        f = '%Y-%m-%d %H:%M:%S'

        values = str(now.strftime(f)), str(decode['md5']), str(mdb.escape_string(path)), str(decoded['md5']), '0', '0'
        insertFile = "INSERT INTO `thugfiles`(`timestamp`, `file_name`, `file_path`, `md5`, `vt_positives`, `vt_total`) VALUES(%s, %s, %s, %s, %s, %s)"

        try:
            logger.debug('Saving thug file info to database')
            self.db_cursor.execute(insertFile, values)
        except mdb.Error, e:
            logger.critical("Error inserting file info into MySQL - %d: %s" % (e.args[0], e.args[1]))

    def handle_payload(self,ident,payload):
        self.ident = ident
        self.payload = payload

        self.save_file(payload)

