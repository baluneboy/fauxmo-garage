#!/usr/bin/env python

# echo_server.py
import sys
import socket

PORT = 12345  # the same port on both machines


def main(txt):
    
    host = ''  # ymbolic meaning all available interfaces
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print '%s got connected to by %s' % (socket.gethostname(), addr)
    
    while True:
        data = conn.recv(1024)
        if not data: break
        data = 'an echo of "%s" PLUS the server, %s, appended "%s"' % (data, socket.gethostname(), txt)
        conn.sendall(data)
        
    conn.close()


if __name__ == '__main__':
    main(sys.argv[1])
