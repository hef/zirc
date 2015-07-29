#!/usr/bin/env python
import configparser
import json
import logging
from pyshorteners.shorteners import Shortener
import re
import rt
import zmq

logging.basicConfig(level='DEBUG')

config = configparser.ConfigParser()
config.read('rotor.ini')

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect(config['zirc']['sub_socket'])
receiver.setsockopt(zmq.SUBSCRIBE, b'')
sender = context.socket(zmq.PUSH)
sender.connect(config['zirc']['push_socket'])

tracker = rt.Rt(config['rt']['rest_endpoint'], config['rt']['user'], config['rt']['password'])
tracker.login()

def rt_id(message):
    match = re.search('!rt ?(\d+)', message)
    if match:
        ticket_id =int(match.group(1))
        results = tracker.search(id=ticket_id, Queue=rt.ALL_QUEUES)
        if len(results) > 0:
            ticket = results[0]
            sender.send_string(format_ticket(ticket))

def format_ticket(ticket):
    shortener = Shortener('IsgdShortener')
    id_number = int(ticket['id'].split('/')[1])
    subject = ticket['Subject']
    queue = ticket['Queue']
    url = shortener.short(config['rt']['url_format'].format(id_number))
    return '\x03{}[PS:One Ping #{}]\x0F {} \x1F{}\x0F'.format(
            config[queue]['color'],
            id_number, 
            subject,
            url
    )

while True:
    message = receiver.recv()
    event = json.loads(message.decode('utf-8'))
    rt_id(event['arguments'][0])

