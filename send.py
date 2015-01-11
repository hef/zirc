#!/usr/bin/env python
import zmq
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='127.0.0.1')
parser.add_argument('message')
args = parser.parse_args()

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect('tcp://{}:5558'.format(args.server))
socket.send_string(args.message)
