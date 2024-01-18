import json
from event_converter import EventConverter
from trace_representation import Event, Trace
import logging
varanus_logger = logging.getLogger("varanus")

""" Abstracts the Mascot's status updates to a trace of events """

class MascotEventAbstractor(EventConverter):
    """Decodes JSON representation of system's status to
    produce a trace of events."""

    def __init__(self, event_map_path):
        super(MascotEventAbstractor, self).__init__()
        # event_map should be a json map path
        with open(event_map_path, "r") as event_map:
            self.event_map = json.load(event_map)
        # TODO Defaults read in from file
        self. last_values = {"velocity": 0, "footswitch": False}

    def _decode_velocity(self, curr_velocity):
        """Decodes the change in velocity. Returns a Trace object """

        # This is an assumption that the speed reading was ok, because the
        # system did it. Otherwise, FDR will reject the trace,
        # which is what we want.
        new_event = Event(str(self.event_map["velocity"]), curr_velocity)
        speed_ok_event = Event("speed_ok", None)

        self.last_values["velocity"] = curr_velocity

        new_trace = Trace([new_event, speed_ok_event])

        return new_trace

    def _decode_footswitch(self, curr_footswitch):
        """ Decodes the change in footswitch. Returns a Trace object """

        new_trace = Trace()

        new_event = Event(self.event_map["footswitch"], curr_footswitch)
        new_trace.add_event(new_event)

        ## Again, assuming that the event we receive was performed correctly
        if curr_footswitch:
            hom_event = Event("enter_hands_on_mode")
            new_trace.add_event(hom_event)
        else:
            am_event = Event("enter_autonomous_mode")
            new_trace.add_event(am_event)

        self.last_values["footswitch"] = curr_footswitch

        return new_trace

    def _decode(self, update):
        """ Decodes the updates in the telegram and returns one more Trace objects """

## Some of this needs to move to convert_to_internal for this implementation
## Decode should be working on the internal representation of CSP events
        curr_velocity = update["velocity"]
        curr_footswitch = update["footswitch"]

        new_trace = None

        # This is hard-coded, needs to be extracted.
        if curr_velocity != self.last_values["velocity"] and curr_footswitch != self.last_values["footswitch"]:
            first_trace_fragment = Trace()
            first_trace_fragment.append_trace(self._decode_velocity(curr_velocity))
            first_trace_fragment.append_trace(self._decode_footswitch(curr_footswitch))

            new_trace_fragment = Trace()
            new_trace_fragment.append_trace(self._decode_footswitch(curr_footswitch))
            new_trace_fragment.append_trace(self._decode_velocity(curr_velocity))


            new_trace = (first_trace_fragment, new_trace_fragment)

        elif curr_velocity != self.last_values["velocity"]:
            # becomes an event
            new_trace = self._decode_velocity(curr_velocity)

        elif curr_footswitch != self.last_values["footswitch"]:
            # becomes an event
            new_trace = self._decode_footswitch(curr_footswitch)
        else:
            # Assume this is just a speed update
            new_trace = self._decode_velocity(curr_velocity)

        return new_trace

    def new_traces(self, update):
        """ Returns the new trace(s) of the system after the update.
        Returns a Trace object """

        # I think this is only useful if the system under monitoring is sending
        # update telgrams (of all the variables)

        new_traces = self._decode(update)
        assert(isinstance(new_traces, tuple) or isinstance(new_traces, Trace))
        # This will be a Trace if we're sure of the order of events
        # or a tuple of Traces if we're not

        if isinstance(new_traces, tuple):
            #first split
            original_trace = self.event_traces[0]
            varanus_logger.debug("Original Trace = " + original_trace)
            varanus_logger.debug("Type of original trace = "+ str(type(original_trace)))

            new_event_traces = []

            for trace in new_traces:

                new_trace = Trace(original_trace)
                new_trace.append_trace(trace)

                new_event_traces.append(new_trace)

            self.event_traces = new_event_traces
        elif len(self.event_traces) > 1 :
            #after first split

            if isinstance(new_traces, tuple):
                #split again
                #TODO
                pass
            else:
                #just update what we have
                for trace in self.event_traces:
                    trace.append_trace(new_traces)


        else:
            #no splits
            self.event_traces[0].append_trace(new_traces)

        return self.event_traces



if __name__ == "__main__":
    ea = MascotEventAbstractor("event_map.json")

    data = (open("../mascot-test/dummy_mascot_data.json"))

    for update in data:
        update_map = json.loads(update)

        varanus_logger.debug("new traces = " + ea.new_traces(update_map))
