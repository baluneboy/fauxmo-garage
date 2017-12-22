#!/usr/bin/env python

# THIS RUNS ON THE MAC

# https://docs.python.org/2/library/socketserver.html

import time
import socket
import threading
import SocketServer

from pims.files.log import my_logger
from foscam_snap import FoscamSnap
from async_socket_common import extract_field_value, AnalysisResults


FOSCAM_INI_FILE = '/Users/ken/config/foscam/cgi_snap.ini'
FOSCAMSNAP = FoscamSnap(FOSCAM_INI_FILE)
logger = my_logger('async_socket_server')


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        logger.info('Do callback with: "%s".' % data)
        result = self.callback(data)
        cur_thread = threading.current_thread()
        #data = '%s,%s=response from server %s' % (result, data, socket.gethostname())
        data = '"%s"' % result
        response = "{} via {}".format(data, cur_thread.name)
        logger.info('Sending response to client: "%s".' % response)
        self.request.sendall(response)
    
    # FIXME this callback is where we do the following:
    #  DONE 1. snap pic from webcam
    #  NEED 2. use opencv or darknet/YOLOv2 to determine real state, open or close
    #  NEED 3. log analysis results, LIKE client_data, client_guessed_state, server_true_state, amt_confidence, result_fname
    def callback(self, client_data):
        """snap picture from webcam, determine real state of garage door (open|close) and log results"""
        # input client_data is comma-delimited string:
        #  SYNTAX: 'wants:STATE,client:NAME'
        # EXAMPLE: 'wants:open,client:pihole'
        fieldstr, want_state = extract_field_value(client_data, 0)
        
        # snap picture with webcam
        fcsnap_fname = FOSCAMSNAP.snap_picture('unknown')
        
        # analyze image from webcam
        image_results = AnalysisResults(fcsnap_fname)
        image_results.compute()
        
        # determine whether or not to trigger garage remote button
        trigger_button = image_results.state != want_state

        return 'seems:%s,trigger_button:%s,median:%d' % (image_results.state, str(trigger_button), image_results.median)        


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
    
    logger.info("Server loop running in thread: %s" % server_thread.name)

    try:
        while True:
            time.sleep(0.25)

    except KeyboardInterrupt:
        logger.info("Server got KeyboardInterrupt in thread: %s" % server_thread.name)
        server.shutdown()
        server.server_close()
        logger.info("Server shutdown and closed.")
        logger.info("--------------------\n")
