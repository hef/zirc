#!/usr/bin/env python
import argparse
import zmq
import fileinput

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='127.0.0.1')
args = parser.parse_args()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{}:5559'.format(args.server))
socket.setsockopt(zmq.SUBSCRIBE, b'')
while True:
    print(socket.recv())

