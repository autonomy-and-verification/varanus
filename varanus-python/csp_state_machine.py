# coding=utf-8
import yaml
import logging

varanus_logger = logging.getLogger("varanus")


class State(object):
    """Represents one state in the Labelled Transition System"""

    def __init__(self, name):
        self.name = name
        self.transitions = {}  # Dictionary: event_name, Transition
        self.has_terminate_transition = False
        self.has_tau = False
        # the alphabet is not given in a yaml file
        # so we assume that only the letters in the obj are the alphabet

    def add_transition(self, transition):
        """Adds a Transition object to this State's list of transitions"""
        if self.transitions is None:
            self.transitions = {}

        self.transitions[transition.name] = transition
        if transition.isTerminate:
            self.has_terminate_transition = True

        if transition.isTau:
            self.has_tau = True

    def transit(self, transition_name):
        """Returns the Transition named transition_name if it is in this State's transition list, or None if it does
        not exist"""
        if transition_name in self.transitions:
            return self.transitions[transition_name]
        else:
            return None

    def __str__(self):
        return self.name


class Transition(object):
    """ Represents a transition between States in the Labelled Transition System
    """
    _TERMINATE = '\xe2\x9c\x93'
    """this is FDR's terminate transition, tick; if we see this we just go to the next state"""

    _TAU = '\xcf\x84'
    """The tau character."""

    _ACCEPTINGSTATE = State('accepting')

    def __init__(self, name):
        self.isTerminate = False
        self.isTau = False
        if name == self._TERMINATE:
            self.isTerminate = True

        if name == self._TAU: # Python is a silly language. This used to use "is" but that fails.
            self.isTau = True
        # Name is the transition is the event that triggers it
        self.name = name
        # TODO Is states only ever one item??
        self.states = {}  # Outgoing states, presumably, or the states that the transition belongs to??
        self.probabilities = {}

    def add_state(self, state):
        """adds the given state to this Transition's list of states"""
        if self.states is None:
            self.states = {}
            self.probabilities = {}

        self.states[state.name] = state
        # TODO Might need to make tau map to a list of destinations
        self.probabilities[state.name] = 1.0

    def get_first_state(self):
        """return the first state in this Transition's list of states """
        if self.isTerminate:
            return self._ACCEPTINGSTATE
        # just return the first state
        return self.states.values()[0]  # ml Why the first state??

    def __str__(self):
        return self.name

class CSPStateMachine(object):
    """
    Represents a state machine of a CSP process/Labelled Transition System. The state machine is built from State objects.
    Each State has a name and a list of transitions.
    Each Transitions has a list of outgoing states.
    """

    _TAU_DEPTH = 5
    # TODO make the below constants useful
    STRICT_MODE = "strict"
    PERMISSIVE_MODE = "permissive"

    def __init__(self, sm_dictionary=None, config_fn=None, mode=None):
        self.states = {}
        self.current_state = None
        self.initial_state = None
        self.explicit_alphabet = False
        self.alphabet = set()

        if config_fn is not None:
            self.load_alphabet_from_config(config_fn)
        else:
            self.config_fn = None

        if sm_dictionary is not None:
            self.load_from_dictionary(sm_dictionary)
        else:
            sm_dictionary = None

        self.mode = mode
        # strict or permissive

    def load_from_dictionary(self, sm_dictionary):
        """
        Loads the information from the sm_dictionary into this State Machine object.
        Each key in sm_dictionary is a state, the values are tuples, each of which is a transition
        """

        for key in sm_dictionary:
            self.add_state(key)

        self.initial_state = self.states['0']

        for key in sm_dictionary:
            for tran in sm_dictionary[key]:
                transition_name = tran[0]
                self.add_letter_to_alphabet(transition_name)
                transition_destination = tran[1]
                self.add_state(transition_destination)
                self.add_transition_by_name(transition_name, key, transition_destination)

    def load_alphabet_from_config(self, config_fn):
        """ Loads the alphabet of the CSP process represented by this State Machine from the config file, which is located at config_fn"""

        with open(config_fn, 'r') as data:
            config = yaml.safe_load(data)

            if 'alphabet' in config:
                self.explicit_alphabet = True
                self.alphabet = set(config['alphabet'])

    def set_initial_state(self, state_name):
        """Makes state_name the initial state"""
        print("state_name type = " + str(type(state_name)))
        print(type(self.states.keys()[0]))
        assert(isinstance(state_name, str))

        if state_name in self.states:
            self.initial_state = self.states[state_name]
            self.current_state = self.initial_state


    def add_state(self, state_name):
        """Adds a state called state_name to the State Machine's list of states"""
        if self.states is None:
            self.states = {}
        if state_name not in self.states:
            self.states[state_name] = State(state_name)  # So...states is a dictionary where the key is the name and the value is the State? Ok, so it's like an index

    def add_letter_to_alphabet(self, letter):
        """Adds the letter to this State Machine's alphabet"""
        if self.alphabet is None:
            self.alphabet = set()
        if self.explicit_alphabet:
            if letter not in self.alphabet:
                varanus_logger.info('Alphabet defined explicitly but new letter found')
        self.alphabet.add(letter)

    def add_transition_by_name(self, transition_name, source_name, destination_name):
        """Adds a transition called transition_name, from source_name to destination_name,
        to this State Machine's list of transitions
        """
        self.add_letter_to_alphabet(transition_name)

        tran = Transition(transition_name)

        if self.states is None:
            self.add_state(source_name)
        if source_name not in self.states:
            self.add_state(source_name)
        if destination_name not in self.states:
            self.add_state(destination_name)
        tran.add_state(self.states[destination_name])
        self.states[source_name].add_transition(tran)

    def log(self, msgprefix, msg):
        """Log the msg to the screen"""
        classprefix = "CSPStateMachine: ".upper()
        print(classprefix + msgprefix.upper() + ": " + msg)

    def get_outgoing_transitions(self):
        """From the current state, return the outgoing transitions"""
        assert (self.current_state is not None)

        outgoing_transitions = self.current_state.transitions
        returned_transitions = []
        for name, destination in outgoing_transitions.items():
            returned_destinations = []
            for destination_name in destination.states:
                returned_destinations.append(destination_name)
            returned_transition = (name, returned_destinations)
            returned_transitions.append(returned_transition)

        return returned_transitions

    def transition(self, transition_name):
        """Takes the transition called transition_name, from the current state"""
        varanus_logger.debug("Transition method. Current State = " + self.current_state.name + " and transition_name = " + transition_name)
        print(transition_name)
        print("$ alphabet = ")
        for a in self.alphabet:
            print(str(a) + " type is " + str(type(a)))

        varanus_logger.info("In state " + self.current_state.name + " saw " + transition_name)

        if self.current_state is None:
            self.current_state = self.initial_state
        if self.current_state.name == "accepting":  # maybe this should be 'terminal' state?
            return self.current_state

        ##if self.current_state.has_terminate_transition: #This is wrong....
        ##    transition_name = Transition._TERMINATE
        ##    self.log("terminal state bypass", "converting transition " + transition_name + " to " + Transition._TERMINATE)
        transition = self.current_state.transit(
            transition_name)  # WHAT IS THIS? This seems to return the transition... as in, 'transit(a)' gives me 'a'
        print("+++ transition returned from  self.current_state.transit(transition_name) = " + str(transition))
        print(self.current_state.has_tau)
        print(self.current_state.name)
        print(str(self.current_state.transitions))
        print("mode = " + str(self.mode))
        if transition is not None:
            varanus_logger.debug("Transition good, moving to next state")
            self.current_state = transition.get_first_state()
        elif self.current_state.has_tau:
            transition = self.explore_taus(transition_name)
            if transition is not None:
                varanus_logger.debug("Transition good, after exploring taus")
                self.current_state = transition.get_first_state()
            else:
                varanus_logger.debug("Transition bad, after exploring taus")
                return None # Still couldn't find a valid transition
        elif self.mode == "strict" : # other situations that could cause this?
            varanus_logger.debug("Transition bad (probably no transition with that name) abort")
            return None # Could not find a transition
        elif self.mode == "permissive":
            # Ignore the event from SUA that is not in the model
            varanus_logger.debug("Saw " + transition_name + " which is not in model alphabet, but mode is permissive, so ignoring")
            return self.current_state

        self.log("NORMAL TRANSITION", "Now in state " + self.current_state.name)
        return self.current_state

    def to_dictionary(self):
        state_dict = {}
        for state in self.states:
            events = []
            for trans in state.transitions.keys:
                events.append(trans.name)

            state_dict[state.name] = events

        return state_dict

    def start(self):
        """Starts the state machine. Sets the current state to be the initial state"""
        self.current_state = self.initial_state
        self.log("explicit_alphabet", str(self.explicit_alphabet))

    def test_machine(self):
        """Simple test of the State Machine class, using simple.csp"""
        result = {}
        self.start()
        transitions = ['a', 'd', 'b', 'c', '\xe2\x9c\x93']
        for transition in transitions:
            if self.current_state.name not in result:
                result[self.current_state.name] = []
            old_state = self.current_state.name

            resulting_state = self.transition(transition)

            if resulting_state is not None:
                result[old_state].append((transition, resulting_state.name))
            else:
                result[old_state].append((transition, resulting_state))

        return result

    def explore_taus(self, transition_name):
        """Explores tau transitions (to _TAU_DEPTH) from the current state to see if the event can be found in subsequent states
        Returns """
        varanus_logger.debug("explore_taus called in state: " + str(self.current_state) + " looking for state that has " + transition_name)
        assert (self.current_state is not None)
        assert (self.current_state.has_tau)

        next_current_state = None
        depth = 0
        state_to_check = self.current_state
        while depth <= self._TAU_DEPTH:
            assert(state_to_check.has_tau) # should handle this better, but it shouldn't fail if the input files are right.
            tau_transition = state_to_check.transitions[Transition._TAU]
            destination = tau_transition.get_first_state()
            print(str(tau_transition))

            next_current_state = destination.transit(transition_name)
            if next_current_state is not None:
                return next_current_state
            else:
                state_to_check = destination
                depth += 1
