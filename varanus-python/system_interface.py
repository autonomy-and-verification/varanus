import socket
from pkgutil import simplegeneric

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

    def parse_ROSMon_event(self, json_line): # probably needs to be user-writen
        """ Decodes a 'full' ROSMon Event, which is a JSON strong from ROS"""
        #  {u'pose': {u'position': {u'y': -3.209985226226464, u'x': 5.392467103672291, u'z': 0.06349744727863198}, u'orientation': {u'y': -1.281609607287051e-06, u'x': 1.4244357144269074e-07, u'z': 0.07116127085777371,
        #  u'w': -0.997464823203427}}, u'value': 38.0, u'topic': u'/radiation_sensor_plugin/sensor_0', u'header': {u'stamp': {u'secs': 161, u'nsecs': 539000000}, u'frame_id': u'sim_sensor', u'seq': 159},
        #  u'verdict': u'currently_true', u'time': 161.539, u'type': u''}

        # This needs to pull out the 'topic' and 'value'
        assert(type(json_line) is str)
        event_list = json.loads(json_line)
        varanus_logger.debug("event_list = " + str(event_list))

        if "topic" not in event_list:
            raise ValueError("Event is missing topic field.")
        else:
            topic_name = event_list['topic']

            if topic_name == "/command":

                if "location" not in event_list:
                    raise ValueError("Event is missing location")

                if "name" not in event_list:
                    raise ValueError("Event is missing name")

                parsed_event = Event(event_list["name"], [event_list["location"]]) 
                print ("SUA Event -> " + topic_name + " with name: " + event_list["name"] + " and location: " + str(event_list["location"]))
            elif topic_name == "/inspected":

                if "location" not in event_list:
                    raise ValueError("Event is missing location")

                parsed_event = Event("inspected", [event_list["location"]]) 
                print ("SUA Event -> " + topic_name + " with location: " + str(event_list["location"]))
            elif topic_name == "/currentLoc":
                parsed_event = Event("arrived_at", [event_list["data"]]) 
                print ("SUA Event -> " + topic_name + " with location: " + str(event_list["data"]))
            elif topic_name == "/radiation_sensor_plugin/sensor_0":
                if "value" not in event_list:
                    raise ValueError("Event is missing value field.")
                else:
                    value = int(event_list["value"])
                    if value >=0 and value < 120 :
                        radiationStatus = "Green"
                    elif value >= 120 and value < 250:
                        radiationStatus = "Orange"
                    elif value >= 250:
                        radiationStatus = "Red"
                    else:
                        raise ValueError("Event has invalid radiation reading")

                    if self.event_map is not None:
                        radiationStatus = self.convert_event(radiationStatus)

                    parsed_event = Event("radiation_level", [radiationStatus])
                    print ("SUA Event -> " + topic_name + " with value: " + str(value))
            else:
                return None # Not a topic we have an event for so filter it

        #if self.event_map is not None:
        #    topic_name = self.convert_event(event_list['topic'])
        #else:
        #    topic_name = event_list['topic']

        #if event_list["value"] is not None:
        #    parsed_event = Event(topic_name, [event_list["value"]])
        #else:
        #    parsed_event = Event(topic_name)
        print("++++ parsed_evet == " +str(parsed_event))

        return parsed_event.to_fdr()




    def parse_simple_ROSMon_event(self, json_line):
        """Decodes a simple ROSMon event from the json file.
        Assumes that there is "data" and a "topic"
        """
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

    def __init__(self, trace_file_path, event_map=None, simple =False):
        SystemInterface.__init__(self) # Python is a silly language. I have to manually make inheritance work...
        self.trace_file_path = trace_file_path
        self._file_open = False
        self.event_map = event_map
        self.events = deque()
        self.trace_file = None
        self.simple=simple

    def connect(self):
        varanus_logger.info("Parsing trace file at: " + self.trace_file_path)
        try:
            # Open the file
            self.trace_file = open(self.trace_file_path)
            self._file_open = True

            line_num = 0
            for json_line in self.trace_file:
                # Loop through, trying to parse using parse_ROSMon_event()
                line_num += 1
                if json_line == '\n':

                    continue
                try:
                    event = self.parse_ROSMon_event(json_line)

                    if event is not None:
                        varanus_logger.debug("appending event " + event)
                        self.events.append(event)
                except ValueError as e:
                    varanus_logger.error("Error parsing trace file on line " + str(line_num) + ": " + str(e))
                    varanus_logger.error("Trace file path: " + self.trace_file_path + "\nAborting")
                    return False

            # If parse_ROSMon_event() has not added any events to the list...
            if len(self.events) == 0 :
                # ... try again with parse_simple_ROSMon_event()
                varanus_logger.debug("parse_ROSMon_event() failed, trying parse_simple_ROSMon_event()")
                self.trace_file.seek(0) # have to 'seek' to the beginning because Python is a little sly
                line_num = 0
                varanus_logger.debug("Looping through file " + str(self.trace_file))
                for json_line in self.trace_file:
                    # Loop through again, trying the simple parser
                    line_num += 1
                    varanus_logger.debug("Trying simple parser on line  " + str(line_num))
                    if json_line == '\n':
                        continue
                    try:
                        event = self.parse_simple_ROSMon_event(json_line)
                        if event is not None:
                            varanus_logger.debug("appending event " + event)
                            self.events.append(event)
                    except ValueError as e:
                        varanus_logger.error("Error parsing trace file on line " + str(line_num) + ": " + str(e))
                        varanus_logger.error("Trace file path: " + self.trace_file_path + "\nAborting")
                        return False
            #Checking again!
            if len(self.events) == 0 :
                # Catchall for if the two parsing methods fail
                varanus_logger.error("Unknown error when parsing trace file: " + self.trace_file_path )
                varanus_logger.error("Aborting")
                return False
        except OSError:
            varanus_logger.error("Trace Path not found during Offline Runtime Verification. trace_file_path=" + str(
                self.trace_file_path))
            return False
        varanus_logger.debug("events len = " + str(len(self.events)))
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

    def __init__(self, message_callback, disconnect_callback, port, IP='127.0.0.1'):
        SystemInterface.__init__(self) # Python is a silly language
        self.IP = IP
        self.port = port

        # init Websocket
        self.server = WebsocketServer(self.port, self.IP)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(disconnect_callback)
        self.server.set_fn_message_received(message_callback)

        varanus_logger.debug(self.server)
        varanus_logger.info("+++ WebSocket Server Initialised +++")

    def send(self, message):
        varanus_logger.info("+++ Sending ", str(message), " +++")
        self.ws.send(message)

    def connect(self):
        self.server.run_forever()

    def new_client(self, client, server):
        """Called for every client connecting (after handshake)"""
        varanus_logger.info("+++ New SUA connected and was given id: " + str(client['id']) + " +++")
        # server.send_message_to_all("Hey all, a new client has joined us")

    def client_left(self, client, server):
        """ Called for every client disconnecting"""
        varanus_logger.info("SUA " + str(client['id']) + " disconnected +++")

    def close(self):
        varanus_logger.debug("WebsocketInterface closed")
        self.server.shutdown()


if __name__ == '__main__':
    system = WebSocketInterface(8080)
    system.connect()
