#!/usr/bin/env python

import logging
from Modules.ShivaParsed import ShivaParsed
from Modules.ThugFiles import ThugFiles

logger = logging.getLogger('artemis')

class BaseHandler(object):

    def __init__(self,ident,db_cursor):
        self.ident = ident
        self.db_cursor = db_cursor
        self.module = None
        self.payload = None

    def select_module(chan):
        if chan is 'shiva.parsed':
            self.module = ShivaParsed(self.db_cursor)
            logger.info('Identified channel as {0}'.format(chan))
        elif chan is 'thug.files':
            self.module = ThugFiles(self.db_cursor)
            logger.info('Identified channel as {0}'.format(chan))
        else:
            logger.info('Could not identify channel {0}'.format(chan))


    def handle_payload(payload):
        logger.debug('Passing payload to handler')
        self.payload = payload
        self.module.handle_payload(self.ident,self.payload)
