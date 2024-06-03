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

    def __init__(self, event_map =None):
        self.event_map = event_map
        pass

    def connect(self):
        pass

    # Perhaps there should be a 'next event' method?
    def next_event(self):
        """Returns the next event from the system """
        pass

    def close(self):
        pass

    def convert_event(self, event_name):
        """Uses the event_map to convert the event name from the version in the trace to the CSP channel name it matches"""
        assert(self.event_map is not None)
        varanus_logger.debug("in _convert_event. event_map = " + str(self.event_map))
        varanus_logger.debug("in _convert_event. event_name = " + str(event_name))

        if event_name in self.event_map:
            return self.event_map[event_name]
        else:
            return event_name

    def parse_ROSMon_event(self, json_line):
        """Decodes a ROSMon event from the json"""
        assert(type(json_line) is str)

        event_list = json.loads(json_line)
        varanus_logger.debug("event_list = " + str(event_list))
        if "data" not in event_list:
            raise ValueError("Event is missing data field.")
        if "topic" not in event_list:
            raise ValueError("Event is missing topic field.")

        # TODO Check if the event in the trace file matches that in the CSP file I was given. CSP State
        #  Machine currently built from main process...so I'm not sure how this will work.
        if self.event_map is not None:
            channel_name = self.convert_event(event_list['topic'])
        else:
            channel_name = event_list['topic']

        if event_list["data"] is not None:
            parsed_event = Event(channel_name, [event_list["data"]])
        else:
            parsed_event = Event(channel_name)

        return parsed_event.to_fdr()





class OfflineInterface(SystemInterface):
    """ Interface to a file of traces."""

    def __init__(self, trace_file_path, event_map=None):
        SystemInterface.__init__(self) # Python is a silly language. I have to manually make inheritance work...
        self.trace_file_path = trace_file_path
        self._file_open = False
        self.event_map = event_map
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
                try:
                    event = self.parse_ROSMon_event(json_line)
                    self.events.append(event)
                except ValueError as e:
                    varanus_logger.error("Error parsing trace file on line " + str(line_num) + ": " + str(e))
                    varanus_logger.error("Trace file path: " + self.trace_file_path + "\nAborting")
                    return False
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

    def __init__(self, port, IP='127.0.0.1'):
        SystemInterface.__init__(self) # Python is a silly language
        self.IP = IP
        self.port = (port)
        self.message_callback = self.websockect_check_event

        # init Websocket
        self.server = WebsocketServer(self.port, self.IP)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_callback)

        varanus_logger.debug(self.server)
        varanus_logger.info("+++ WebSocket Server Initialised +++")

    def send(self, message):
        varanus_logger.info("+++ Sending ", str(message), " +++")
        self.ws.send(message)

    def connect(self):
        self.server.run_forever()

    def websockect_check_event(self, client, server, message):
        """Called when a client sends a message, callback method"""
        varanus_logger.debug("Monitor got: " + message)
        print(type(message))

        # decode the event from the messge
        decoded = self.parse_ROSMon_event(str(message)) # message is unicode
        varanus_logger.debug("Monitor decoded message: " + decoded)

            # then check the event against the state machine
            # which we do already in run_offline_state_machine() (here)
            # this also needs extracting and testing


    def new_client(self, client, server):
        """Called for every client connecting (after handshake)"""
        varanus_logger.info("+++ New ROS monitor connected and was given id: " + str(client['id']) + " +++")
        # server.send_message_to_all("Hey all, a new client has joined us")

    def client_left(self, client, server):
        """ Called for every client disconnecting"""
        varanus_logger.info("ROS monitor " + str(client['id']) + " disconnected +++")

    def close(self):
        self.server.close()


if __name__ == '__main__':
    system = WebSocketInterface(8080)
    system.connect()
