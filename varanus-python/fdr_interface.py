import os
import platform
import sys
import logging
from csp_state_machine import CSPStateMachine

varanus_logger = logging.getLogger("varanus")

""" Interface to FDR.
 FDR API Usage Example file that I've reused and edited.
Original file available at: https://cocotec.io/fdr/manual/_downloads/ffcc2113bd60df5a33677f5bbe5193da/command_line.py (2019-08-21)
"""

if platform.system() == "Linux":
    for bin_dir in os.environ.get("PATH", "").split(":"):

        fdr4_binary = os.path.join(bin_dir, "fdr4")
        if os.path.exists(fdr4_binary):
            real_fdr4 = os.path.realpath(os.path.join(bin_dir, "fdr4"))

            # Added by Matt Luckcuck 2019-08-21

            # Take the fdr4 real dir, go up two steps...
            upone = os.path.split(real_fdr4)
            uptwo = os.path.split(upone[0])

            # ... join with lib and append to path
            sys.path.append(os.path.join(uptwo[0], "lib"))
            # hasta lasagna don't get any on ya
            break
elif platform.system() == "Darwin":
    for app_dir in ["/Applications", os.path.join("~", "Applications"), "/Users/user/programs"]:
        if os.path.exists(os.path.join(app_dir, "FDR4.app")):
            sys.path.append(os.path.join(
                app_dir, "FDR4.app", "Contents", "Frameworks"))
            break

# from command_line import *
import fdr


class FDRInterface(object):
    """Interfaces the monitor with FDR"""

    def __init__(self):
        fdr.library_init()

        self.session = fdr.Session()

    def load_model(self, model_path):
        """Loads the csp model at modelPath into the current session"""

        assert (self.session is not None)

        try:
            self.session.load_file(model_path)

        except fdr.Error as e:
            varanus_logger.error(e)

    def _make_assertion(self, trace):
        # generate assert and dump it into the model
        assert_start = "MASCOT_SAFETY_SYSTEM  :[has trace]: <"
        assert_end = ">"

        varanus_logger.debug("type of trace: " + str(type(trace)))

        assert_check = assert_start
        trace_list = trace.to_list()
        varanus_logger.debug("trace_list: " + str(trace_list))

        for i in range(len(trace_list)):
            # the str is key here. My editor produced unicode which became
            # a unicode object, not a str object so the assertion parsing broke.
            event = str(trace_list[i])
            varanus_logger.debug("event: " + event)
            varanus_logger.debug("event type: " + str(type(event)))
            assert_check = assert_check + event
            if i < len(trace_list) - 1:
                assert_check = assert_check + ", "
            elif i == len(trace_list) - 1:
                assert_check = assert_check + assert_end

        return assert_check

    def _run_assertion(self, assertion_string):
        """ Runs the given assertion in the existing FDR session
        """
        varanus_logger.debug("+++ running assertion: " + assertion_string)
        assert (self.session is not None)

        parsed_assert = self.session.parse_assertion(assertion_string)
        assertion = parsed_assert.result()
        assertion.execute(None)

        return assertion

    def check_determinism(self, process, events_to_hide):
        """ Checks if the given process is deterministic after hiding the given events
        """
        assert(isinstance(process, str))
        assert(isinstance(events_to_hide, set))

        events_list = ",".join(events_to_hide)

        assertion_string =  process + "\{|" + events_list + "|} :[deterministic]:"

        assertion = self._run_assertion(assertion_string)

        if assertion.passed():
            varanus_logger.info("+++ " + process + " is monitorable, continuing +++")
            return True
        else:
            varanus_logger.error("+++ " + process + " is not monitorable, while hiding " +  events_list + " ABORTING +++")
            return False




    def check_trace(self, trace):
        """ parses the trace and executes it in the current session.
            returns True if the assertion passed or
            False if the assertion fails """

        assert (self.session is not None)

        assertion_string = self._make_assertion(trace)
        varanus_logger.debug("assertion_string: " + assertion_string)

        assertion = self._run_assertion(assertion_string)

        if assertion.passed():
            varanus_logger.info("+++ " + assertion.to_string() + " Passed +++")
            return True
        else:
            varanus_logger.info("+++ " + assertion.to_string() + " Failed +++")

            for counterexample in assertion.counterexamples():
                # describe_counterexample(self.session, counterexample, children=False)
                # Matt: 9th of Jan 24 -> Not sure what describe_counterexample is... so I suppose:
                pass

            return False

    def convert_to_state_machine(self, process):
        """ Makes a state machine object from the process"""

        # This evaluates a process (say, the trace)
        LTS = self.session.evaluate_process(process, fdr.SemanticModel_Traces, None)

        # The result of the evaluate_process call is a state machine
        machine = LTS.result()
        root = machine.root_node()
        state_machine = CSPStateMachine()

        self.build_state_machine(machine, state_machine, root)


        return state_machine

    def build_state_machine(self, csp_machine, state_machine, this_node):
        """Explores the csp_machine, building the states and transitions of the sate_machine as it goes. It starts
        with this_node and recurses."""

        # Get the alphabet
        alpha = csp_machine.alphabet(False)
        print("* alphabet from csp_machine = ")
        for a in alpha:
            print(self.session.uncompile_event(a))
            state_machine.add_letter_to_alphabet(str(self.session.uncompile_event(a)))

        varanus_logger.info("Building CSP State Machine")
        self.explore_states(csp_machine, [], state_machine, this_node)
        print("-")
        print(len(state_machine.states))
        print(str(state_machine.states))
        print(str(this_node.hash_code()))
        print(type(state_machine.states[str(this_node.hash_code())]))
        print("-")
        state_machine.set_initial_state(str(this_node.hash_code()))  # Sets the state_machine's initial and current state
        print("initial = " + str(type(state_machine.initial_state)))
        print("current =" + str(type(state_machine.current_state)))
        # Also, Python is a silly language; setting this internal variable should not be possible.
        varanus_logger.info("CSP State Machine Built")
        return state_machine

    def explore_states(self, csp_machine, visited, state_machine, this_node):
        visited.append(this_node)
        transitions = csp_machine.transitions(this_node)
        destinations_list = []
        for t in transitions:
            # Get the destination (node) of this transition and
            # if it's not already in the list of destination, add it.
            # destinations is the list we use to recurse on.
            destination = t.destination()

            if destination not in visited:
                destinations_list.append(destination)

            # String name of the next state (will be an integer)
            next_state = str(destination.hash_code())
            # String name of the event
            event = str(self.session.uncompile_event(t.event()))

            # String name of this state (again, will be an integer)
            this_node_num = str(this_node.hash_code())
            print("In node " + this_node_num)

            # Add the (event, destination) pair to the state machine
            state_machine.add_transition_by_name(event, this_node_num, next_state)
        # Recurse for each destination of this_node
        for d in destinations_list:
            print("Checking " + str(d))
            self.explore_states(csp_machine, visited, state_machine, d)
        varanus_logger.debug("explore_states returning...")

    def convert_to_dictionary(self, process):
        """
        Makes a dictionary from the process
        """

        # This evaluates a process (say, the trace)
        LTS = self.session.evaluate_process(process, fdr.SemanticModel_Traces, None)

        # The result of the evaluate_process call is a state machine
        machine = LTS.result()
        root = machine.root_node()

        # process_map = get_events(fdr_interface, machine, root)
        process_map = self.build_process_map(machine, root)

        return process_map

    # Currently just doing strings
    def build_process_map(self, csp_machine, this_node):
        """
        Gets, what I've called a process map for the CSP process (the csp_machine).
        It starts with the this_node, gets the events and destinations, then recurses.
        """

        transitions = csp_machine.transitions(this_node)
        machine_map = {}
        destinations = []
        print("Building Process Map")
        for t in transitions:
            # Get the destination (node) of this transition and
            # if it's not already in the list of destination, add it.
            # destinations is the list we use to recurse on.
            destination = t.destination()
            if destination not in destinations:
                destinations.append(destination)

            # String name of the next state (will be an integer)
            next_state = str(destination.hash_code())
            # String name of the event
            event = str(self.session.uncompile_event(t.event()))

            # String name of this state (again, will be an integer)
            this_node_num = str(this_node.hash_code())
            print("In node " + this_node_num)

            # Add the (event, destination) pair to the map
            if this_node_num in machine_map.keys():
                current_list = machine_map[this_node_num]
                current_list.append((event, next_state))
                machine_map.update({this_node_num: current_list})
            else:
                machine_map.update({this_node_num: [(event, next_state)]})

        # Recurse for each destination of this_node
        for d in destinations:
            print("Checking " + str(d))
            machine_map.update(self.build_process_map(csp_machine, d))

        return machine_map

    def new_session(self):
        self.close()
        self.session = fdr.Session()

    def close(self):
        fdr.library_exit()
