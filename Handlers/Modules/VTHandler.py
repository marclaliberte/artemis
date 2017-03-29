#!/usr/bin/env python
import json
import hashlib
import logging
from virus_total_apis import PublicApi as vtPubAPI
import MySQLdb as mdb

logger = logging.getLogger('artemis')

class VTHandler():
    def __init__(self,vt_api_key,db_cursor,table):
        self.api_key = vt_api_key
        self.db_cursor = db_cursor
        self.table = table
        self.vt = vtPubAPI(self.api_key)
        logger.debug("VTHandler initialized")

    def get_hash(self,file_path):
        try:
            md5_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            logger.debug("File MD5 Generated: %s" % md5_hash)
        except Exception, e:
            logger.critical("Error generating MD5 for file: %s" % e)
        return md5_hash

    def save_vt_count(self,md5,date,positives,total):
        values = (date,int(positives),int(total),md5)
        updateRecord = "UPDATE " + self.table + " SET `last_vt` = %s, `vt_positives` = %s, `vt_total` = %s WHERE `md5` = %s"
        try:
            self.db_cursor.execute(updateRecord, values)
            logger.info("Updated database entry for %s" % str(md5))
        except mdb.Error, e:
            logger.critical("Error updating attachment database - %d: %s" % (e.args[0], e.args[1]))

    def check_hash(self,md5_hash):
        try:
            response = self.vt.get_file_report(md5_hash)
            logger.debug("Response received from VirusTotal")
        except Exception, e:
            logger.critical("Error querying VirusTotal %s" % e)

        if(response['response_code'] == 200): 
            vtCounter = 0
            vtPositives = 0
            results = response['results']
            if (results['response_code'] == 1):
                logger.info("File has previous scan data")
                scan_date = results['scan_date']
                scans = results['scans']
                for key,value in scans.iteritems():
                    vtCounter += 1
                    if (value['detected'] == True):
                        vtPositives += 1

                logger.info("VirusTotal dection count %d" % vtCounter)
                self.save_vt_count(md5_hash,scan_date,vtPositives,vtCounter)
            else:
                logger.info("File has no previous scan data")
        else:
            logger.error("VirusTotal query failed")

    def new_file(self,file_path):
        md5_hash = self.get_hash(file_path)
        self.check_hash(md5_hash)



if __name__ == '__main__':
    handler = VTHandler('8daa039c612f8fe8706176c54faabf85d6e4caae8deaa579446fe149384df3bb')
    handler.new_file('/var/artemis/files/attachment/424fd08a4a35a003381db727c61a6c32-a-Glossary_Updates.docx')

