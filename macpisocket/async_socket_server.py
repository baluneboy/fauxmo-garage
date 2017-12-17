#!/usr/bin/env python

# THIS RUNS ON THE MAC

# https://docs.python.org/2/library/socketserver.html

import time
import socket
import threading
import SocketServer

from foscamsnap import snap_pic


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        result = self.callback(data)
        cur_thread = threading.current_thread()
        data = '%s,%s=response from server %s' % (result, data, socket.gethostname())
        response = "{} via {}".format(data, cur_thread.name)
        self.request.sendall(response)
    
    # FIXME this callback is where we do the following:
    #  DONE 1. snap pic from webcam
    #  NEED 2. use opencv or darknet/YOLOv2 to determine true state, open or close
    #  NEED 3. log analysis results, LIKE client_data, client_guessed_state, server_true_state, amt_confidence, result_fname
    def callback(self, client_data):
        # input client_data is comma-delimited string:
        #  SYNTAX: 'GUESSED
        #           STATE,------DATETIME------------,CLIENT'
        # EXAMPLE: 'close,2017-12-17 08:15:23.018234,pihole'
        guessed_state = client_data.split(',')[0]
        fname1 = snap_pic(guessed_state)
        time.sleep(5)  # placeholder for analysis routine
        return '%s' % fname1.upper()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":

    HOST, PORT = "192.168.1.103", 9998  # zero for port (2nd item) to select arbitrary unused port

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    print "Server loop running in thread:", server_thread.name
    
    try:
        while True:
            time.sleep(0.25)

    except KeyboardInterrupt:   
        server.shutdown()
        server.server_close()
