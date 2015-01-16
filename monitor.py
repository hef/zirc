#!/usr/bin/env python
import argparse
import json
from pprint import pprint
import zmq

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='127.0.0.1')
parser.add_argument('--port', default=5556)
args = parser.parse_args()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{}:{}'.format(args.server, args.port))
socket.setsockopt(zmq.SUBSCRIBE, b"")

while True:
    topic, message = socket.recv_multipart()
    data = json.loads(message.decode('utf-8'))
    print(topic)
    pprint(data)



