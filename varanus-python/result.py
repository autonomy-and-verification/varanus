
class Result(object):
    #TODO integrate Time_Store

    def __init__(self):

        self.passed = None
        self.error_state = None
        self.trace = None
        self.expected_events = None

    def trace_passed(self):
        self.passed= True
        self.error_state = None
        self.trace = None
        self.expected_events = None

    def trace_failed(self, error_state, trace, expected_events):
        self.passed = False
        self.error_state = error_state
        self.trace = trace
        self.expected_events = expected_events

    def __str__(self):
        assert(self.passed is not None)

        if self.passed:
            return "Trace file finished with no violations"
        else:
            return "System Violated the Specification with Trace: " + str(self.trace) + "\n" + \
                    "This node expected the following events: " + str(self.expected_events)


