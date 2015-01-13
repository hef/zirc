#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pprint import pprint
import zmq
import cgi
import json


class ZMQHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        postvars = {}
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            content = self.rfile.read(length).decode('utf-8')
            postvars = cgi.parse_qs(content, keep_blank_values=1)
        
        message = {}
        message['client_address'] = self.client_address
        message['command'] = self.command
        message['path'] = self.path
        message['request_version'] = self.request_version
        message['form'] = postvars
        data = json.dumps(message)
        self.server.zmq_socket.send_multipart([ self.path.encode('utf-8') ,data.encode('utf-8')])
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('',8000), ZMQHandler)
    context = zmq.Context.instance()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://*:5556')
    server.zmq_socket = socket
    server.serve_forever()

