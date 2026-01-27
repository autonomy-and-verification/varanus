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
* `trace-json-fail-safety` is `trace-json-good`, using the Orange radiation spike to show the safety requirement being ignored.
* `trace-json-fail-message-order` swaps the order of `move` and `inspect` (so now `inspect` comes first) to show that out-of-order ROS messages will be caught. The error is on line 166 and 194. This should be caught in 'strict' mode.
* `trace-json-fail-param-mismatch` has move.1 and then arrived_at.3 (the `current_loc` ROS message ) on line 93

There are config files for both the RoboChart and CSP versions of the model.

* `config_rover_pass.yaml` and `config_robochart_pass.yaml` run the offline checks against `trace-json-pass` so should pass.
* `config_rover_fail_safety.yaml` and `config_robochart_fail_safety.yaml` run the offline checks against `trace-json-fail-safety` and should fail because an Orange-level of radiation is ignored
* `config_rover_fail_ordering.yaml` and `config_robochart_fail_ordering.yaml` runs the offline checks against `trace-json-fail-message-ordering` and should fail because move and inspect are out of order
* `config_rover_fail_param_mismatch.yaml` and `config_robochart_fail_param_mismatch.yaml` run the offline checks against `trace-json-fail-safety` and should fail because it is moving to waypoint 1 but arrives at waypoint 3.

## Experiments

The experiments are timed runs of Varanus using each of the eight config files, four for the RoboChart version of the model and four for the CSP version. Varanus was run 10 times for each config file, with the results logged into `log/ras-results`. The paper reports the average of the build, checking, and total times.
