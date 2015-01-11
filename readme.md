zirc is a daemon that connects to an IRC server, joins a channel, and listens for zmq push messages on port 5558

    pip install -r requirements.txt
    python3 zirc.py --nick zirc --server irc.freenode.net --channel #botwars


Sending Messages
================

    echo "Hello, World!" | python3 send.py
