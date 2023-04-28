class State(object):
    def __init__(self, name):
        self.name = name
        self.transitions = None
        self.has_terminate_transition = False
        # the alphabet is not given in a yaml file
        # so we assume that only the letters in the obj
        # are the alphabet

    def add_transition(self, transition):
        if self.transitions is None:
            self.transitions = {}

        self.transitions[transition.name] = transition
        if transition.isterminate:
            self.has_terminate_transition = True

    def transit(self, tranname):
        if tranname in self.transitions:
            return self.transitions[tranname]
        else:
            return None

    def __str__(self):
        return self.name


class Transition(object):
    # this is fdrs terminate transition
    # if we see this we just go to the next state
    _TERMINATE = '\xe2\x9c\x93'
    _ACCEPTINGSTATE = State('accepting')

    def __str__(self):
        return self.name

    def __init__(self, name):
        self.isterminate = False
        if (name == self._TERMINATE):
            self.isterminate = True
        self.name = name
        self.states = None
        self.probabilities = None

    def add_state(self, state):
        if self.states is None:
            self.states = {}
            self.probabilities = {}
        self.states[state.name] = state
        self.probabilities[state.name] = 1.0

    def get_first_state(self):
        if self.isterminate:
            return self._ACCEPTINGSTATE
        # just return the first state
        return self.states.values()[0]


# the class for creating a "state machine from a dictionary"
# states have names and transitions
# transitions have states
class CSPStateMachine(object):

    def __init__(self):
        self.states = None
        self.current_state = None
        self.initial_state = None
        self.explicit_alphabet = False
        self.alphabet = None

    def __init__(self, sm_dictionary, config_fn=None):
        self.states = None
        self.current_state = None
        self.initial_state = None
        self.explicit_alphabet = False
        self.alphabet = None
        if config_fn is not None:
            self.load_alphabet_from_config(config_fn)
        self.create_from_dictionary(sm_dictionary)

    def create_from_dictionary(self, sm_dictionary):
        # so this is a state machine dictionary
        # all the keys are states
        # all the tuples are transitions
        for key in sm_dictionary:
            self.add_state(key)

        self.initial_state = self.states['0']

        for key in sm_dictionary:
            for tran in sm_dictionary[key]:
                tranname = tran[0]
                self.add_letter_to_alphabet(tranname)
                trandest = tran[1]
                self.add_state(trandest)
                self.add_transition_by_name(key, tranname, trandest)

    def load_alphabet_from_config(self, config_fn):
        import yaml
        with open(config_fn, 'r') as data:
            config = yaml.safe_load(data)

            if 'alphabet' in config:
                self.explicit_alphabet = True
                self.alphabet = set(config['alphabet'])

    def init_state(self, statename):
        if statename in self.states:
            self.initial_state = self.states[statename]

    def add_state(self, statename):
        if self.states is None:
            self.states = {}
        if statename not in self.states:
            self.states[statename] = State(statename)

    def add_letter_to_alphabet(self, letter):
        if self.alphabet is None:
            self.alphabet = set()
        if self.explicit_alphabet:
            if letter not in self.alphabet:
                print('Alphabet defined explicitly but new alphabet found')
        self.alphabet.add(letter)

    def add_transition_by_name(self, srcname, tranname, destname):
        self.add_letter_to_alphabet(tranname)

        tran = Transition(tranname)

        if self.states is None:
            self.add_state(srcname)
        if srcname not in self.states:
            self.add_state(srcname)
        if destname not in self.states:
            self.add_state(destname)
        tran.add_state(self.states[destname])
        self.states[srcname].add_transition(tran)

    def log(self, msgprefix, msg):
        classprefix = "CSPStateMachine: ".upper()
        print(classprefix + msgprefix.upper() + ": " + msg);

    def transit(self, tranname):

        if self.current_state is None:
            self.current_state = self.initial_state
        if self.current_state.name == "accepting":
            return self.current_state

        if self.current_state.has_terminate_transition:
            tranname = Transition._TERMINATE
            self.log("terminal state bypass", "converting transtion " + tranname + " to " + Transition._TERMINATE)
        transition = self.current_state.transit(tranname)
        if transition is not None:
            self.current_state = transition.get_first_state()
        else:
            # if the alphabet is explicit
            # we will assume that anything we have seen in the alphabet
            # that we dont have a transition for is BAD
            logmsg = "In state " + self.current_state.name + " saw " + tranname

            if self.explicit_alphabet:

                if tranname in self.alphabet:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Stated alphabet", "returning bad state i.e. None - saw bad event")

                    return None

            else:
                if tranname in self.alphabet:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Stated alphabet", "returning bad state i.e. None - saw bad event")

                    return None
                else:
                    self.log("UNEXPECTED TRANSITION", logmsg)
                    self.log("Inferred alphabet", "returning current state i.e. ignoring event")
                    return self.current_state

        return self.current_state

    def start(self):
        self.current_state = self.initial_state

    def test_machine(self):
        result = {}
        self.start()
        transitions = ['a', 'd', 'b', 'c', '\xe2\x9c\x93']
        for transition in transitions:
            if (self.current_state.name not in result):
                result[self.current_state.name] = []
            oldstate = self.current_state.name

            resstate = self.transit(transition)

            if resstate is not None:
                result[oldstate].append((transition, resstate.name))
            else:
                result[oldstate].append((transition, resstate))

        return result
