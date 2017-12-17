#!/usr/bin/env python

import os
import sys
import wget
import datetime
from ConfigParser import SafeConfigParser


def snap_pic(state):
    
    # get parameters to build URL for CGI snap picture from foscam
    ini_file = '/Users/ken/config/foscam/cgi_snap.ini'
    parser = SafeConfigParser()
    parser.read(ini_file)
    ip_addr = parser.get('cgi_snap', 'ip_address')
    port = parser.get('cgi_snap', 'port')
    uname = parser.get('cgi_snap', 'username')
    passwd = parser.get('cgi_snap', 'password')
    outdir = parser.get('cgi_snap', 'outdir')
    
    # build URL from config file parameters
    URL = "http://%s:%s/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=%s&pwd=%s" % (ip_addr, port, uname, passwd)
    
    # build output filename and snap image
    bname = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '_' + state + '.jpg'
    fname = os.path.join(outdir, bname)
    filename = wget.download(URL, fname, False)
    return filename

    
if __name__ == '__main__':
    state = sys.argv[1]
    fname = snap_pic(state)
    print "open -a Firefox %s &" % fname
