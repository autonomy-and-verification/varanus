from state_machine import *
from CSPStateMachine import CSPStateMachine

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
    # this is a dictionary where the key is the node number
    # the value is a list of tuples (transition, dest)

    statemachine_wrapper = CSPStateMachine(result2)

    print("result...")
    print(result2)
    assert (result2 == test_process2_sm)

    wrapper_result = statemachine_wrapper.test_machine()
    print("result from wrapper ")
    print(wrapper_result)
    # print(test_process3)
    # result3 = (make_simple_state_machine(test_process3))
    # print("result...")
    # print(result3)
    # assert(result3 == test_process3_sm)
