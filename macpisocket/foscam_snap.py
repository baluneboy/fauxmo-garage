#!/usr/bin/env python

import os
import sys
import wget
import datetime
from ConfigParser import SafeConfigParser


class FoscamSnap(object):
    
    def __init__(self, ini_file):
        if not os.path.exists(ini_file):
            raise Exception('ini_file "%s" does not exist' % ini_file)
        self.ini_file = ini_file
        self.ip_address = None
        self.port = None
        self.output_dir = None
        self._username = None
        self._password = None
        self._cgi_url = None
        self._read_config()

    def _read_config(self):
        """read config file parameters and build cgi url needed to wget a snapped image"""
        parser = SafeConfigParser()
        parser.read(self.ini_file)
        self.ip_address = parser.get('cgi_snap', 'ip_address')
        self.port = parser.get('cgi_snap', 'port')
        self.output_dir = parser.get('cgi_snap', 'outdir')        
        self._username = parser.get('cgi_snap', 'username')
        self._password = parser.get('cgi_snap', 'password')
        self._url = "http://%s:%s/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=%s&pwd=%s" % (
                                                                                        self.ip_address,
                                                                                        self.port,
                                                                                        self._username,
                                                                                        self._password)
    
    def snap_picture(self, state):
        """build output filename, snap image and return filename"""
        bname = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '_' + state + '.jpg'
        fname = os.path.join(self.output_dir, bname)
        filename = wget.download(self._url, fname, False)
        return filename

    
def demo():
    state = sys.argv[1]
    ini_file = '/Users/ken/config/foscam/cgi_snap.ini'
    fcsnap = FoscamSnap(ini_file)
    fcsnap_fname = fcsnap.snap_picture(state)
    print "open -a Firefox %s &" % fcsnap_fname


if __name__ == '__main__':
    demo()