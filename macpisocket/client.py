#!/usr/bin/env python

import sys
import socket

PORT = 12345  # the same port on both machines


def main(txt):
    
    # define server connection params (that is, the "other" machine)
    this_machine = socket.gethostname()
    #print "this_machine is %s" % this_machine
    
    if this_machine == 'macmini3.local':
        host = 'pihole' # the server
    elif this_machine == 'pihole':
        host = 'macmini3'
    else:
        raise Exception('unhandled local machine name %s' % this_machine)
        
    # establish socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, PORT))
    s.sendall(b'%s sent from %s' % (txt, socket.gethostname()))
    data = s.recv(1024)
    s.close()
    print 'the client, %s, received' % socket.gethostname(), repr(data)


if __name__ == '__main__':
    main(sys.argv[1])
