import socket
from websocket_server import WebsocketServer
from mascot_event_abstractor import MascotEventAbstractor
import json
import logging
varanus_logger = logging.getLogger("varanus")

"""Communicates with the system being monitored and passes back its handle.
This should provide a common interface to the Monitor class, regardless of the
system's underlying connection  """


class SystemInterface(object):
    """Interface for all system interfaces"""

    def __init__(self):
        pass

    def connect(self):
        pass

    # Perhaps there should be a 'next event' method?

    def close(self):
        pass


class OfflineInterface(SystemInterface):
    """ Interface to a file of traces."""

    def __init__(self, trace_file_path, event_map = None):
        self.trace_file_path = trace_file_path
        if event_map != None:
            self.EventAbs = EventAbstractor(event_map)

    def connect(self):
        self.trace_file = open(self.trace_file_path)
        return self.trace_file

    def close(self):
        self.trace_file.close()

class TCPInterface(SystemInterface):
    """Interface to a TCP connection."""

    def __init__(self, IP, port, event_map = None):
        self.IP = IP
        self.port = port

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.IP, self.port))
        s.listen(1)

        self.conn, addr = s.accept()
        varanus_logger.debug("+++ Varanus Connection address: "+ str(addr))
        return self.conn

    def close(self):
        self.conn.close()


class TCPInterface_Client(TCPInterface):
    """Interface to a TCP connection, as a Client """

    def connect(self):
        self.varanus_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.varanus_socket.connect((self.IP, self.port))

        return self.varanus_socket

    def close(self):
        self.varanus_socket.close()



class WebSocketInterface(SystemInterface):
    """ Interface to a WebSocket Connection, runs a WebSocket Server """

    def __init__(self, message_callback, port, IP='127.0.0.1'):
        self.IP = IP
        self.port = (port)


        # init Websocket
        self.server = WebsocketServer(self.port, self.IP)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(message_callback)

        varanus_logger.debug(self.server)
        varanus_logger.info("+++ WebSocket Server Initialised +++")

    def send(self, message):
        varanus_logger.info("+++ Sending ", message, " +++")
        self.ws.send(message)

    def connect(self):
        self.server.run_forever()

    def new_client(self, client, server):
        """Called for every client connecting (after handshake)"""
        varanus_logger.info("+++ New ROS monitor connected and was given id: "+ client['id'] + " +++" )
        # server.send_message_to_all("Hey all, a new client has joined us")

    def client_left(self, client, server):
        """ Called for every client disconnecting"""
        varanus_logger.info("ROS monitor "+ client['id'] +" disconnected +++"  )

    def close(self):
        self.server.close()


if __name__ == '__main__':
    system = WebSocketInterface(8080)
    system.connect()
