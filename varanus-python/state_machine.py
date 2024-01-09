"""
Utilities for turning CSPm into useful State Machines

Matt Luckcuck 2022
"""
from fdr_interface import *


def make_simple_state_machine(process, fdr_interface = None):
    """
    Makes a state machine from the process
    """
    if fdr_interface is None:
        fdr_interface = FDRInterface()
        # This loads the whole model (channels and all)
        fdr_interface.load_model("test/simple.csp")


    # This evaluates a process (say, the trace)
    LTS = fdr_interface.session.evaluate_process(process, fdr.SemanticModel_Traces, None)

    # The result of the evaluate_process call is a state machine
    machine = LTS.result()
    root = machine.root_node()

    # process_map = get_events(fdr_interface, machine, root)
    process_map = get_process_map(fdr_interface, machine, root)

    fdr_interface.close()

    return process_map


# Currently just doing strings
def get_process_map(fdr_interface, machine, this_node):
    """
    Gets, what I've called a process map for the CSP process (the machine).
    It starts with the this_node, gets the events and destinations, then recurses.
    """

    transitions = machine.transitions(this_node)
    machine_map = {}
    destinations = []

    for t in transitions:
        # Get the destination (node) of this transition and
        # if it's not already in the list of destination, add it.
        # destinations is the list we use to recurse on.
        destination = t.destination()
        if destination not in destinations:
            destinations.append(destination)

        # String name of the next state (will be an integer)
        next_state = str(destination.hash_code())
        # String name of the event
        event = str(fdr_interface.session.uncompile_event(t.event()))

        # String name of this state (again, will be an integer)
        this_node_num = str(this_node.hash_code())
        print("In node " + this_node_num)

        # Add the (event, destination) pair to the map
        if (this_node_num in machine_map.keys()):
            current_list = machine_map[this_node_num]
            current_list.append((event, next_state))
            machine_map.update({this_node_num: current_list})
        else:
            machine_map.update({this_node_num: [(event, next_state)]})

    # Recurse for each destination of this_node
    for d in destinations:
        print("Checking " + next_state)
        machine_map.update(get_process_map(
            fdr_interface, machine, d))

    return machine_map


# This is the old method I wrote before
def get_events(fdr_interface, machine, this_node):

    transitions = machine.transitions(this_node)
    transition_pairs = []
    for t in transitions:
        # the event the transition represents
        trans_event = fdr_interface.session.uncompile_event(t.event())

        print(trans_event)
        dest = t.destination()  # the node the transition goes to
        print("hash code = " + str(dest.hash_code()))
        # and the events out of the destination
        initials_dest = machine.initials(dest)
        next_events = fdr_interface.session.uncompile_events(
            initials_dest)  # tuple
        print(next_events)

        for e in next_events:
            transition_pairs.append((trans_event.to_string(), e.to_string()))
            print(transition_pairs)
        if(next_events):
            transition_pairs += get_events(fdr_interface, machine, dest)

    return transition_pairs


if __name__ == '__main__':

    # Make some test processes
    test_process = "a -> b -> SKIP"
    test_process_sm = {'0': [('a', '1')], '1': [('b', '2')], '2': [
                              ('\xe2\x9c\x93', '3')]}

    test_process2 = "a -> (b -> SKIP [] c -> SKIP)"
    test_process2_sm = {'0': [('a', '1')], '1': [("b", '2'), ("c", "2")], '2': [
                               ('\xe2\x9c\x93', '3')]}

    test_process3 = "(b -> SKIP [] c -> SKIP)"
    test_process3_sm = {'1': [('\xe2\x9c\x93', '2')], '0': [
                               ('b', '1'), ('c', '1')]}

# Run some tests. I've only been able to test one process at a time, becasue
# after one it segfaults...

#    print(test_process)
#    result = make_simple_state_machine(test_process)
#    print("result...")
#    print(result)
#    assert (result == test_process_sm)

    print(test_process2)
    result2 = (make_simple_state_machine(test_process2))
    print("result...")
    print(result2)
    assert(result2 == test_process2_sm)

    # print(test_process3)
    # result3 = (make_simple_state_machine(test_process3))
    # print("result...")
    # print(result3)
    # assert(result3 == test_process3_sm)
