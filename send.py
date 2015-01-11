#!/usr/bin/env python
import argparse
import zmq
import fileinput

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='127.0.0.1')
args = parser.parse_args()

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect('tcp://{}:5558'.format(args.server))

with fileinput.input(files=('-')) as f:
    for line in f:
        socket.send_string(line)
