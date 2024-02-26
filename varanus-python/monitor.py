from fdr_interface import FDRInterface
from system_interface import *
from event_converter import *
from rosmon_mascot_event_abstractor import *
from mascot_event_abstractor import *
from trace_representation import Event, Trace
from csp_state_machine import CSPStateMachine
import state_machine
import json
import time
import logging
import yaml

# "MASCOT_SAFETY_SYSTEM :[has trace]: <system_init>"
# "model/mascot-safety-system.csp"
varanus_logger = logging.getLogger("varanus")


class Monitor(object):
    """The main class of the program, controls the process """

    def __init__(self, model_path, config_file, event_map_path=None):
        self.fdr = FDRInterface()
        self.model_path = model_path
        self.fdr.load_model(self.model_path)
        # TODO This will need to be fixed later. Possibly Monitor should be instantiated with an Event Mapper
        # self.eventMapper = MascotEventAbstractor(event_map_path)
        if event_map_path is None:
            self.event_map = None
        else:
            with open(event_map_path, "r") as event_map:
                self.event_map = json.load(event_map)

        self.explicit_alphabet = False
        self.alphabet = []
        self.config_file = config_file
        if config_file is not None:
            self.load_alphabet_from_config(config_file)

    def load_alphabet_from_config(self, config_fn):
        """ Loads the alphabet of the CSP process represented by this State Machine from the config file, which is located at config_fn"""

        with open(config_fn, 'r') as data:
            config = yaml.safe_load(data)

            if 'alphabet' in config:
                self.explicit_alphabet = True
                self.alphabet = set(config['alphabet'])

    def new_fdr_session(self):
        assert (self.fdr != None)
        self.fdr.new_session()

    def load_fdr_model(self, model_path):
        self.fdr.load_model(self.model_path)

    def build_state_machine(self, main_process, alphabet=None):
        """Builds a CSPStateMachine object for the main_process with the given alphabet"""

        print("! main process = " + str(main_process))
        print("! model path = " + str(self.model_path))
        # dict_sm = (self.fdr.convert_to_dictionary(main_process))
        process = self.fdr.convert_to_state_machine(main_process)  # CSPStateMachine(dict_sm, self.config_file)
        return process

    def check_result(self, event, result):
        # if the alphabet is explicit
        # we will assume that anything we have seen in the alphabet
        # that we don't have a transition for is BAD
        print("check_result: " + str(event) + " and " + str(result))
        print(str(self.alphabet))
        if result is None:
            if self.explicit_alphabet:

                if event not in self.alphabet:  # this is the wrong condition
                    varanus_logger.info("UNEXPECTED TRANSITION")
                    varanus_logger.info("Stated alphabet returning bad state i.e. None - saw bad event")

                    return False
                else:
                    varanus_logger.info("unexpected transition:")
                    varanus_logger.info(
                        "Stated alphabet returning bad state i.e. None - event not available in this state")
                    return False

            else:
                if event not in self.alphabet:
                    varanus_logger.info("UNEXPECTED TRANSITION: ")
                    varanus_logger.info("Inferred alphabet returning bad state i.e. None - saw bad event")

                    return False
                else:
                    varanus_logger.info("UNEXPECTED TRANSITION")
                    varanus_logger.info("Inferred alphabet returning current state i.e. ignoring event")
                    return True
        else:
            return True

    def _run_offline_state_machine(self, main_process, trace_path):
        """ Runs Varanus offline, on a file of traces, using the State Machine representation of the CSP Process"""
        varanus_logger.info("+++ Running Offline -- Using State Machine +++")

        process = self.build_state_machine(main_process)

        process.start()
        # test_result = process.test_machine()
        result = {}

        # Extract the Traces and start the loop
        monitored_system = OfflineInterface(trace_path, self.event_map)
        is_connected = monitored_system.connect()
        if not is_connected:
            varanus_logger.error("Could not open trace_file at: " + trace_path)
            return
        trace = Trace()

        varanus_logger.info("Checking trace file: " + trace_path)
        while monitored_system.has_event():
            varanus_logger.debug("self.event_map is None = " + str(self.event_map is None))

            event = monitored_system.next_event()
            varanus_logger.debug("event = " + event)
            trace.add_event(Event(event))

            if process.current_state.name not in result:
                result[process.current_state.name] = []
            old_state = process.current_state.name

            resulting_state = process.transition(event)  # This returns None if there is no available transition
            print("resulting_state = " + str(resulting_state))

            if self.check_result(event, resulting_state):
                result[old_state].append((event, resulting_state.name))
            else:
                result[old_state].append((event, resulting_state))
                varanus_logger.error("System Violated the Specification with Trace: " + str(trace.to_list()))
                varanus_logger.error("This node expected the following events: " + str(
                    process.get_outgoing_transitions()))  # TODO make this even prettier
                print(type(result))
                print(str(result))
                return result  # So far, return because a None means it's bad.

        varanus_logger.info("Trace file finished with no violations")
        return result  # this is not caught, not sure if I need to return anything

    def _run_offline_traces_single(self, trace_path):  # deprecated
        """ Runs Varanus Offline, taking a single trace and sending it to FDR"""

        varanus_logger.info("+++ Running Offline Traces Single +++")

        system = OfflineInterface(trace_path)
        trace_file = system.connect()
        trace = Trace()

        # Take a single line
        trace_line = trace_file.read()
        # parse to list
        event_list = json.loads(trace_line)
        varanus_logger.debug("event_list:" + str(event_list))

        # build trace from list
        for event in event_list:
            event = str(event)
            if event.find(".") == -1:
                channel, params = event, None
                new_event = Event(channel, params)
                trace.add_event(new_event)
            else:
                channel, params = event.split(".", 1)
                new_event = Event(channel, params)
                trace.add_event(new_event)

        varanus_logger.debug("trace: " + str(trace))

        # throw at FDR
        print("before check_trace")
        result = self.fdr.check_trace(trace)
        varanus_logger.debug("result: " + str(result))

        if not result:
            system.close()
            return result

        return result

    # This Doesn't Work As Expected.
    # Takes last event from each line and accumulates
    # so we get a failure:
    # MASCOT_SAFETY_SYSTEM
    #    :[has trace]: <system_init, speed.1250, protective_stop, speed_ok> Failed
    # Counterexample type: minimal acceptance refusing {safe_stop_cat1, }
    # Obvious bullshit
    def _run_offline_traces(self, log_path):  # Deprecated
        system = OfflineInterface(log_path)

        trace_file = system.connect()
        trace = Trace()

        for json_line in trace_file:
            if json_line == '\n':
                continue
            varanus_logger.debug("json_line:" + json_line)
            # No convert_to_internal here because it's for a file of traces
            event_list = json.loads(json_line)
            varanus_logger.debug("event_list" + str(event_list))
            last_event = event_list[-1]
            varanus_logger.debug("last_event" + last_event)

            if last_event.find(".") == -1:
                channel, params = last_event, None
                event = Event(channel, params)
                trace.add_event(event)
            else:
                channel, params = last_event.split(".", 1)
                event = Event(channel, params)
                trace.add_event(event)

            varanus_logger.debug("trace: " + str(trace) + "and type: " + type(trace))

            result = self.fdr.check_trace(trace)
            varanus_logger.debug("result: " + result)

            if not result:
                system.close()
                return result

        return result

    def run_offline_rosmon(self, log_path):
        system = OfflineInterface(log_path)

        # get the trace file
        trace_file = system.connect()
        trace = Trace()

        # check the traces
        for json_line in trace_file:
            if json_line == '\n':
                continue

            varanus_logger.debug("json_line" + json_line)

            event_map = self.eventMapper.convert_to_internal(json.loads(json_line))

            varanus_logger.debug("event_map: " + str(event_map))
            #### THIS IS A BAD PLACE FOR THIS
            event = Event(event_map["channel"], event_map["params"])
            trace.add_event(event)
            varanus_logger.debug("event: " + event)

            if event_map["channel"] == "speed":
                speed_ok = Event("speed_ok")
                trace.add_event(speed_ok)

            if event_map["channel"] == "foot_pedal_pressed" and event_map["params"] == True:
                mode_change = Event("enter_hands_on_mode")
                trace.add_event(mode_change)
            elif event_map["channel"] == "foot_pedal_pressed" and event_map["params"] == False:
                mode_change = Event("enter_autonomous_mode")
                trace.add_event(mode_change)

            ####

            # trace = eventMapper.new_traces(event)

            varanus_logger.debug("trace: " + trace)
            ###############

            result = self.fdr.check_trace(trace)
            varanus_logger.debug("result: " + result)

            if not result:
                system.close()
                return result

        return result

    def run_online_traces_accumulate(self, ip, port, timeRun=False):
        """Accepts events transferred across a socket, accumulates a trace,
        and for each new event checks the new trace in FDR. """

        varanus_logger.info("+++ Running Offline Traces Single +++")
        ##connect to the system
        system = TCPInterface_Client(ip, port)
        conn = system.connect()

        trace = Trace()

        if timeRun:
            time_list = []
            t0 = time.time()

        # How to terminate? What is the end program signal?
        while 1:

            # get the data from the system
            data = conn.recv(1024)
            # break if it's empty
            if not data: break

            varanus_logger.info("+++ Varanus received: " + data + " +++")
            conn.send(data)  # echo

            if data.find(".") == -1:
                channel, params = data, None
                new_event = Event(channel, params)
                trace.add_event(new_event)
            else:
                channel, params = data.split(".", 1)
                new_event = Event(channel, params)
                trace.add_event(new_event)

            # Send to FDR
            result = self.fdr.check_trace(trace)
            # result = True

            varanus_logger.debug("result: " + str(result))

            if timeRun:
                t1 = time.time()
                total = t1 - t0
                time_tuple = (trace.get_length(), total)
                time_list.append(time_tuple)

        conn.close()
        if timeRun:
            varanus_logger.info("Times:")
            for t in time_list:
                varanus_logger.info(str(t))
        system.close()

    def run_online(self, ip, port):

        ##connect to the system
        system = TCPInterface(ip, port)
        conn = system.connect()

        # How to terminate? What is the end program signal?
        while 1:

            # get the data from the system
            data = conn.recv(1024)
            # break if it's empty
            if not data: break

            varanus_logger.debug("received data:" + str(data))
            conn.send(data)  # echo

            new_traces = self.eventMapper.new_traces(json.loads(data))
            varanus_logger.debug("new_traces: " + new_traces)

            results = []
            for new_trace in new_traces:
                varanus_logger.debug("new_trace: " + new_trace)
                result = self.fdr.check_trace(new_trace)

                varanus_logger.debug("result: " + result)
                results.append(result)

            num_of_results = len(results)
            num_of_t = 0
            for r in results:
                if r:  # is true
                    num_of_t = num_of_t + 1

            percentage_true = (float(num_of_t) / num_of_results) * 100

            if percentage_true == 0:
                varanus_logger.info("False (100%)")
            else:
                varanus_logger.info("True (" + str(percentage_true) + "%)")
        # TODO if we get to here: UnboundLocalError: local variable 'result' referenced before assignment

        return result

    def run_online_websocket(self, ip, port):
        """ Run as an Online Monitor, connecting via WebSocket """

        ##connect to the system
        system = WebSocketInterface(self.websockect_check_event, port)
        system.connect()
        # conn = system.connect()

    def websockect_check_event(self, client, server, message):
        """Called when a client sends a message, callback method"""
        varanus_logger.debug("Monitor got: " + message)

        json_original_message = json.loads(str(message))
        for key in json_original_message.keys():
            tmp = json_original_message[key]
            del json_original_message[key]
            json_original_message[str(key)] = tmp

        json_reply_message = json_original_message

        new_traces = self.eventMapper.new_traces(json_original_message)
        varanus_logger.debug("new_traces: " + new_traces)

        results = []
        for new_trace in new_traces:
            varanus_logger.debug("new_traces: " + new_trace)
            result = self.fdr.check_trace(new_trace)

            varanus_logger.debug("result: " + result)
            results.append(result)

        num_of_results = len(results)
        num_of_t = 0
        for r in results:
            if r:  # is true
                num_of_t = num_of_t + 1

        percentage_true = (float(num_of_t) / num_of_results) * 100

        if percentage_true == 0:
            varanus_logger.info("False (100%)")
            json_reply_message["error"] = True
        else:
            varanus_logger.info("True (" + str(percentage_true) + "%)")
            json_reply_message["error"] = False

        varanus_logger.debug("Monitor Sending " + json_reply_message)
        server.send_message(client, str(json_reply_message))

        # if check_event(message):
        #     server.send_message(client, message)
        # else:
        #     message_dict['error'] = True
        #     message_dict['spec'] = property.PROPERTY
        #     server.send_message(client, json.dumps(message_dict))

    def close(self):

        self.fdr.close()

    def run_state_machine_test(self, main_process):

        dict_sm = (state_machine.make_simple_state_machine(main_process, fdr_interface=self.fdr))
        # this is a dictionary where the key is the node number
        # the value is a list of tuples (transition, dest)

        CSPsm = CSPStateMachine(dict_sm)

        scenario1_events = ["a", "b"]
        scenario2_events = ["a", "c", "b"]
        scenario3_events = ["test", "a", "b"]

        print("Testing Scenario 1...")
        for event in scenario1_events:
            CSPsm.transition(event)

        print("Testing Scenario 2...")
        for event in scenario2_events:
            CSPsm.transition(event)

        print("Testing Scenario 3...")
        for event in scenario3_events:
            CSPsm.transition(event)
