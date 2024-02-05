import socket
from websocket_server import WebsocketServer
from trace_representation import Event, Trace
from mascot_event_abstractor import MascotEventAbstractor
from rosmon_mascot_event_abstractor import *
from mascot_event_abstractor import *
import json
import logging
from collections import deque

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
    def next_event(self):
        """Returns the next event from the system """
        pass

    def close(self):
        pass


class OfflineInterface(SystemInterface):
    """ Interface to a file of traces."""

    def __init__(self, trace_file_path, event_map=None):
        self.trace_file_path = trace_file_path
        self._file_open = False
        #if event_map != None:
        #    self.EventAbs = EventAbstractor(event_map)
        self.events = deque()

    def connect(self):
        varanus_logger.info("Parsing trace file at: " + self.trace_file_path)
        try:
            trace_file = open(self.trace_file_path)
            self._file_open = True
            line_num = 0
            for json_line in trace_file:
                line_num += 1
                if json_line == '\n':
                    continue
                event_list = json.loads(json_line)
                varanus_logger.debug("event_list = " + str(event_list))
                if "data" not in event_list:
                    varanus_logger.error(
                        "Event object on line " + str(line_num) + " in the trace file is missing the data field.\n"
                        "Trace file path: " + self.trace_file_path + "\nIf there is no data, use \"data\": null\n Aborting")
                    return False

                if "topic" not in event_list:
                    varanus_logger.error("Event object on Line " + str(line_num) + " in the trace file is missing the "
                        "topic field.\nTrace file path: " + self.trace_file_path + "\n Aborting")
                    return False

                # TODO Check if the event in the trace file matches that in the CSP file I was given. CSP State
                #  Machine currently built from main process...so I'm not sure how this will work.
                if event_list["data"] is not None:
                    parsed_event = Event(event_list['topic'], [event_list["data"]])
                else:
                    parsed_event = Event(event_list["topic"])

                event = parsed_event.to_fdr()
                self.events.append(event)


        except OSError:
            varanus_logger.error("Trace Path not found during Offline Runtime Verification. trace_file_path=" + str(
                self.trace_file_path))
            return False

        varanus_logger.info("Parsed trace file OK")
        return True # Connected ok

    def has_event(self):
        if not self._file_open:
            self.connect()
        if not self.events:
            return False
        else:
            return True

    def next_event(self):
        if not self._file_open:
            self.connect()
        return self.events.popleft()

    def close(self):
        self.trace_file.close()


class TCPInterface(SystemInterface):
    """Interface to a TCP connection."""

    def __init__(self, IP, port, event_map=None):
        self.IP = IP
        self.port = port

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.IP, self.port))
        s.listen(1)

        self.conn, addr = s.accept()
        varanus_logger.debug("+++ Varanus Connection address: " + str(addr))
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
        varanus_logger.info("+++ New ROS monitor connected and was given id: " + client['id'] + " +++")
        # server.send_message_to_all("Hey all, a new client has joined us")

    def client_left(self, client, server):
        """ Called for every client disconnecting"""
        varanus_logger.info("ROS monitor " + client['id'] + " disconnected +++")

    def close(self):
        self.server.close()


if __name__ == '__main__':
    system = WebSocketInterface(8080)
    system.connect()
