# Inspection Rover (RAS)

This is the version of the Inspection Rover example used for the paper in the Robtocis and Autonomous Systems journal.

## RoboChart Model

## CSP Model

## Configs and Traces

There are two trace files generated from the simulation:
* `trace-json-good` - Cut short Has four Orange radiation spikes, as the rover crosses the storage area, but they seem to be in four different runs.
* `trace-json-bad`

Then we have the trace files that we used for the timed runs:

* `trace-json-pass` is a modified version of `trace-json-good`, where all the radiation results are green. Specifically modified the values on line 40 so that the "value" parameter is lower than 120 (Orange radiation).
* `trace-json-fail-safety` is `trace-json-good`, using the organge radiation spike to show the safety requirement being ignored.
* `trace-json-fail-message-order` swaps the order of move and inspect (so now inspect comes first) to show that out-of-order ROS messages will be caught. The error is on line 166 and 194. This should be caught in 'strict' mode.
* `trace-json-fail-param-mismatch` has move.1 and then arrived_at.3 (actually `current_loc` on line 93
