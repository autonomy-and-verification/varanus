# Basic Entry Point Details 

This is a high-level description of the 'entry point' to Varanus to make it run online.

## Classes and Methods

* `varanus.py`: this is the main module/file, it parses the command line arguments and sets up constants 
  - entry point for the program, `main` code is located at the bottom of the file
  - the `run()` method is an `if`/`else` structure that runs the type of operation that the user specified in the `type` argument, either: 'offline', 'online', 'sm-test', 'offline-test', 'stress-test', or 'build-only'
  - `run()` is where the timing starts and stops
  - `run()` instantiates `Monitor` and called on of its `run...` methods
* `Monitor`: the main class of the program, controls the process
  - `__init__()`: must be given `model_path` and `config_file` 
  - `run_online(ip, port)`: connects to the given port and IP address using TCP. This has not been tested for a long time so might not work anymore
  - `run_online_websocket(ip, port)`: connects to the port and IP address using Websockets. This is more recent, I wrote this, and its related methods, last time we were trying to get Varanus working online with ROSMon
  - `websockect_check_event(client, server, message)`: callback message for `run_online_websocket`, it was built to check an event transmitted via the Websocket. Line `505` tries to take the transition on the model that is labelled by the `event`, this is checked on line `509` by `check_result(event, resulting_state)
  - `check_result(event, result)`: used by all the modes to check if the `result` state after taking a transition labelled by `event` is a passing or failing event, given where in the model we are. I do not think that this version of check_result()` has been tested with `websockect_check_event`. If you need to alter this, I suggest making a new method to ensure that we don't break the other modes.

### Call Chain  

For starting Varanus online, we run: `python varanus-python/varanus.py online config.yaml`.

This calls:
* `varanus.py`'s `__main__` code, which calls 
* `varanus.py`'s `run()` method, which calls
* `Monitor.__init__()`, then `run()` calls
* `Monitor.run_online_websocket()`

When a message comes through the WebSocket, it calls
* `Monitor.websockect_check_event()`, which calls
* `CSPStateMachine.transition(event)` to try to perform the transition labelled by `event`, then calls
* `Monitor.check_result(event, resulting_state)` to check the result of the `transition()` method.


