#!/usr/bin/env python

# THIS RUNS ON THE RPi

import sys
import socket
import datetime

from pims.files.log import my_logger


class CommaSeparatedMessage(object):
    
    def __init__(self, message):
        if ',' in message: raise Exception('message to be formatted cannot itself contain commas')
        self.message = message
        self.datetime = datetime.datetime.now()
        self.hostname = socket.gethostname()
        
    def __str__(self):
        return ','.join([self.message, str(self.datetime), self.hostname])


def send_to_server(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall('%s' % message)        
        response = sock.recv(1024)
        print "{}".format(response)
    finally:
        sock.close()


if __name__ == "__main__":

    # this is client (typically running on RPi)

    # FIXME with argparse to get state info
    
    # establish logger
    logger = my_logger('async_socket_client')
    
    # set ip and port of the server
    ip, port = '192.168.1.103', 9998

    # get state info to be: { unknown | open | close }
    if len(sys.argv) == 1:
        msg = 'unknown'
    elif len(sys.argv) > 2:
        raise Exception("too many inputs; requires either zero or one arg")
    elif sys.argv[1] in ['open', 'close', 'unknown']:
        msg = sys.argv[1]
    else:
        raise Exception("invalid arg; must be among: {'open'|'close'|'unknown'}")
    
    # send formatted message to server
    csm = CommaSeparatedMessage(msg)
    logger.info('Sending comma-separated message to server: "%s"' % csm)
    send_to_server(ip, port, csm)
