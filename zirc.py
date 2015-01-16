#!/usr/bin/env python
import argparse
import logging
import time
import irc.bot
from irc.client import Connection, Event, Reactor
import zmq

log = logging.getLogger(__name__)

class ZMQReactor(Reactor):

    def zmq_pull(self):
        """Creates and returns a ServerConnection object."""

        c = ZMQConnection(self)
        with self.mutex:
            self.connections.append(c)
        return c

    def process_once(self, timeout=0):
        log.log(logging.DEBUG-2, "process_once()")
        sockets = self.sockets
        if sockets:

            # build a list of socket fd's to real sockets
            socket_objects = filter(lambda s: hasattr(s, 'fileno'), sockets)
            socket_index = dict(map(lambda s: (s.fileno(), s), socket_objects))
            # zmq.select is going to return zmq sockets and socket fds
            (i, o, e) = zmq.select(sockets, [], [], timeout)

            # rebuild fd's into socket objects, and also keep zmq sockets
            active_sockets = []
            for entry in i:
                if entry in socket_index:
                    active_sockets.append(socket_index[entry])
                else:
                    active_sockets.append(entry)
            self.process_data(active_sockets)
        else:
            time.sleep(timeout)
        self.process_timeout()


class ZMQConnection(Connection):

    socket = None

    def __init__(self, reactor):
        super(ZMQConnection, self).__init__(reactor)
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.bind('tcp://0.0.0.0:5558')

    def process_data(self):
        string = self.socket.recv_string()
        event = Event('zmq_recv', 'zmq', 'zmq', string)
        self._handle_event(event)

    def _handle_event(self, event):
        self.reactor._handle_event(self, event)


class ZircBot(irc.bot.SingleServerIRCBot):

    def __init__(self, nickname, server, port, channel):
        self.reactor_class = ZMQReactor
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(server, port)],
            nickname,
            nickname
        )
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(self.get_nickname() + '_')

    def on_welcome(self, c, e):
        c.join(self.channel)

    def zmq_pull(self):
        self.reactor.zmq_pull()

    def on_zmq_recv(self, c, e):
        message = e.arguments.splitlines()[0][:250]
        print(message)
        self.connection.privmsg(self.channel, message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', required=True)
    parser.add_argument('--server', required=True)
    parser.add_argument('--port', type=int, default=6667)
    parser.add_argument('--channel', required=True)
    parser.add_argument('--log', dest='level', action='store')
    args = parser.parse_args()

    logging.basicConfig(level=args.level)

    bot = ZircBot(
        nickname=args.nick,
        server=args.server,
        port=args.port,
        channel=args.channel
    )
    bot.connection.set_rate_limit(1)
    bot.zmq_pull()
    bot.start()
