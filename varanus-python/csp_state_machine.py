import yaml


class State(object):
    """Represents one state in the Labelled Transition System"""

    def __init__(self, name):
        self.name = name
        self.transitions = {}
        self.has_terminate_transition = False
        # the alphabet is not given in a yaml file
        # so we assume that only the letters in the obj
        # are the alphabet

    def add_transition(self, transition):
        """Adds a Transition object to this State's list of transitions"""
        if self.transitions is None:
            self.transitions = {}

        self.transitions[transition.name] = transition
        if transition.isTerminate:
            self.has_terminate_transition = True

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
    _ACCEPTINGSTATE = State('accepting')

    def __init__(self, name):
        self.isTerminate = False
        if name == self._TERMINATE:
            self.isTerminate = True
        # Name is the transition is the event that triggers it
        self.name = name
        self.states = {} # Outgoing states, presumably
        self.probabilities = {}

    def add_state(self, state):
        """adds the give state to this Transition's list of states"""
        if self.states is None:
            self.states = {}
            self.probabilities = {}

        self.states[state.name] = state
        self.probabilities[state.name] = 1.0

    def get_first_state(self):
        """return the first state in this Transition's list of states """
        if self.isTerminate:
            return self._ACCEPTINGSTATE
        # just return the first state
        return self.states.values()[0]

    def __str__(self):
        return self.name



class CSPStateMachine(object):
    """
    Represents a state machine of a CSP process/Labelled Transition System. The state machine is built from State objects.
    Each State has a name and a list of transitions.
    Each Transitions has a list of outgoing states.
    """

    def __init__(self, sm_dictionary=None, config_fn=None):
        self.states = {}
        self.current_state = None
        self.initial_state = None
        self.explicit_alphabet = False
        self.alphabet = None

        if config_fn is not None:
            self.load_alphabet_from_config(config_fn)
        else:
            self.config_fn = None

        if sm_dictionary is not None:
            self.load_from_dictionary(sm_dictionary)
        else:
            sm_dictionary = None

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

    def initial_state(self, state_name):
        """Makes state_name the initial state"""
        if state_name in self.states:
            self.initial_state = self.states[state_name]

    def add_state(self, state_name):
        """Adds a state called state_name to the State Machine's list of states"""
        if self.states is None:
            self.states = {}
        if state_name not in self.states:
            self.states[state_name] = State(state_name)

    def add_letter_to_alphabet(self, letter):
        """Adds the letter to this State Machine's alphabet"""
        if self.alphabet is None:
            self.alphabet = set()
        if self.explicit_alphabet:
            if letter not in self.alphabet:
                print('Alphabet defined explicitly but new alphabet found')
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

    def transition(self, transition_name):
        """Takes the transition called transition_name, from the current state"""

        self.log("checking transition", transition_name)

        if self.current_state is None:
            self.current_state = self.initial_state
        if self.current_state.name == "accepting":
            return self.current_state

        if self.current_state.has_terminate_transition:
            transition_name = Transition._TERMINATE
            self.log("terminal state bypass", "converting transition " + transition_name + " to " + Transition._TERMINATE)
        transition = self.current_state.transit(transition_name)
        if transition is not None:
            self.current_state = transition.get_first_state()
        else:
            # if the alphabet is explicit
            # we will assume that anything we have seen in the alphabet
            # that we dont have a transition for is BAD
            logmsg = "In state " + self.current_state.name + " saw " + transition_name

            if self.explicit_alphabet:

                if transition_name in self.alphabet:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Stated alphabet", "returning bad state i.e. None - saw bad event")

                    return None

            else:
                if transition_name in self.alphabet:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Stated alphabet", "returning bad state i.e. None - saw bad event")

                    return None
                else:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Inferred alphabet", "returning current state i.e. ignoring event")
                    return self.current_state

        return self.current_state

    def start(self):
        """Starts the state machine. Sets the current state to be the initial state"""
        self.current_state = self.initial_state

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
