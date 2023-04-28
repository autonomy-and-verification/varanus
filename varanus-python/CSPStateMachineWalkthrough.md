# A walkthrough of the class called CSPStateMachine
### Files used: 
* `wrap_state_machine.py`
* `CSPStateMachine.py` 
* `state_machine.py`
* `sm_config.yaml`

### Walkthrough 
#### `wrap_state_machine.py`
This does all the work, so this is the bit I will attempt to explain. 
* Assuming we have a CSP process `a->b->SKIP` 
* We can use `make_simple_state_machine` from `state_machine` to generate a dictionary representation of the FDR TS. 
* This dictionary contains all the states as keys and a list of transition-state pairs as values i.e. each state has a list of tranistion-state pairs associated with it. 
* We can then create a `CSPStateMachine` object initialised using this dictionary
* **The constructor simply assumes that the first state it adds to it's list is the initial state**
* Through this object we can: 
  * set an initial state 
  * add states 
  * add transitions 
  * apply transitions 

#### `CSPStateMachine.py` 
This file has 3 classes:State,Transition and CSPStateMachine 

##### State 
* constructor takes in a state name
* `add_transition` adds a transition to the state (expected object `Transition`)
* `transit` takes an *event* or *transition name* and returns the corresponding transition object or None 

##### Transition 
* construction takes the name, if the name matches a tick then this is a terminating transition
* `add_state` adds a state to the transition with probability 1 
* `get_first_state` returns the first state of a transtion 
* Also has a class variable `_ACCEPTINGSTATE` of type `State` with the name accepting 

##### Config file 
> This is not a class but can be fed to the CSPStateMachine class. 
The contents of the config file are simple. 
* alphabet: a list of the alphabet/events in the CSPStateMachine 


##### CSPStateMachine 
This class uses a config file to configure the state machine. 
* constructor -> empty where everything is set to None or False / calls `create_from_dictionary` (additional optional argument, a config file )
* The constructor also creates a list of the _alphabet_. This is either input from the config file or derived from the transitions in the dictionary. 

* The object assumes the following (see `transit` function):
  * If the config file has an alphabet, `explicit_alphabet` is `True` 
  * Therefore when a state-transition pair does not exist AND the transition seen is part of the alphabet, the object returns `None` in order to signal a bad event 
  * If the config file does not have an alphabet then when a state-transition pair does not exist AND the transition is part of the inferred alphabet, then too we return `None` to signal a bad event i.e we know this event will happen but we did not expect it to happen right now 
  * In the case the transition is not part of the inferred alphabet the current state is returned

> Usage: see `test_machine` in CSPStateMachine for usage 

## TODO
* add a function that returns a dictionary from a CSPStateMachine object (so we can create from a dictionary and generate one too if needed) 

