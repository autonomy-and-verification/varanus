
_TERMINATE = '\xe2\x9c\x93'
"""this is FDR's terminate transition, tick; if we see this we just go to the next state"""

_TAU = '\xcf\x84'
"""The tau character."""
class CSPLTS(object):

    def __init__(self, name = None, states = None):
        if name is None:
            self.name = "CSP LTS"
        else:
            self.name = name

        if states is None:
            self.states = {}
        else:
            self.states = states

    def add_state(self, name):
        new_state = State(name)
        self.states[name] = new_state


class State(object):

    def __init__(self, name, transitions = None):
        self.name = name

        if transitions is None:
            transitions = {}


