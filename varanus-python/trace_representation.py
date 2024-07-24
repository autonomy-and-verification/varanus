import logging

varanus_logger = logging.getLogger("varanus")

""" Represents traces and event within the program """


class Event(object):
    """"Represents one CSP Event"""

    def __init__(self, channel, parameters=None):
        """ Constructs an event on the given channel communicating the given parameters """
        self.channel = str(channel)
        self.suaEvent = ""

        if parameters is not None and type(parameters) != type([]):
            self.parameters = [parameters]
        else:
            self.parameters = parameters

    def to_fdr(self):

        fdr_string = self.channel
        varanus_logger.debug("to_fdr, parameter = " + str(self.parameters))
        if self.parameters is not None:
            for p in self.parameters:
                fdr_string = fdr_string + "." + str(p)

        return fdr_string

    def __str__(self):
        out = "Event: " + self.channel

        if self.parameters is not None:
            for p in self.parameters:
                out = out + "." + str(p)

        return out


class Trace(object):
    """ Represents a single CSP trace """

    def __init__(self, initial_trace=None):
        # starts as the empty trace
        if initial_trace == None:
            self.trace = []
        elif type(initial_trace) == type([]):
            self.trace = initial_trace
        elif isinstance(initial_trace, Event):
            self.trace = [initial_trace]
        elif isinstance(initial_trace, Trace):
            varanus_logger.debug("append initial trace: " + initial_trace)
            self.trace = []
            self.append_trace(initial_trace)
        else:
            assert (not isinstance(initial_trace, tuple))
            self.trace = [Event(initial_trace)]
            varanus_logger.debug("initial trace: " + initial_trace)
            varanus_logger.debug("type of initial trace: " + str(type(initial_trace)))
            varanus_logger.debug("trace is: " + str(self.trace))

    def add_event(self, new_event):
        """ Adds an event to the trace """
        assert (new_event != None)
        assert (not isinstance(new_event, Trace))
        assert (isinstance(new_event, Event))

        self.trace.append(new_event)

    def get_trace(self):
        """ Returns the trace as a list """
        return self.trace

    def get_length(self):
        """Returns the length of the trace """
        return len(self.trace)

    def append_trace(self, new_trace):
        """ Appends the events in a trace object to this trace """

        for event in new_trace.get_trace():
            self.add_event(event)

    def to_list(self):
        """ Returns a list of the events in the trace """

        fdr_list = []
        for event in self.trace:
            fdr_list.append(event.to_fdr())

        return fdr_list

    def __str__(self):
        out = "Trace: [ "
        trace_len = len(self.trace)
        count = 0
        for event in self.trace:
            count = count + 1
            out = out + str(event)

            if count < trace_len:
                out = out + " ,"
        out = out + " ]"
        return out


if __name__ == "__main__":
    e1 = Event("speed", 100)
    e2 = Event("system_init")

    print(e1.to_fdr())
    print(e2.to_fdr())

    t1 = Trace()
    print(t1.to_list())
    t1.add_event(e1)
    print(t1.to_list())

    t2 = Trace(e2)
    print(t2.to_list())

    print(e1)
    print(e2)
    print(t1)
    print(t2)
