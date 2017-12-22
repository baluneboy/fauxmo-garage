#!/usr/bin/env python

# THIS RUNS ON THE RPi

import ast
import sys
import socket

from pims.files.log import my_logger
from async_socket_common import extract_field_value


class CommaSeparatedMessage(object):
    
    def __init__(self, message):
        if ',' in message: raise Exception('message to be formatted cannot itself contain comma')
        self.message = message
        self.hostname = socket.gethostname()
        
    def __str__(self):
        what = 'wants:%s' % self.message
        who = 'client:%s' % self.hostname
        return ','.join([what, who])


def send_to_server(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall('%s' % message)        
        logger.info('Sent a message to server: "%s"' % message)
        response = sock.recv(1024)
        logger.info("Response from the server: {}".format(response))
    finally:
        sock.close()
    
    # extract result from response, which shows server analysis
    fieldstr, triggerstr = extract_field_value(response, 1)
    trigger_button = ast.literal_eval(triggerstr)

    return trigger_button


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
    trigger = send_to_server(ip, port, csm)
    logger.info('Trigger actions: %s' % str(trigger))
