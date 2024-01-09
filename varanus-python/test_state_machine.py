from fdr_interface import FDRInterface
from csp_state_machine import *

if __name__ == "__main__":
    print("+++ Testing CSP State Machine Class Built from Dictionary +++")
    fdr = FDRInterface()
    fdr.load_model("../sm-test/simple.csp")
    main_process = "a -> (b -> SKIP [] c -> SKIP)"
    config_file = "../sm-test/sm_test.yaml"
    dict_sm = (fdr.convert_to_dictionary(main_process))
    process = CSPStateMachine(dict_sm, config_file)
    test_result = process.test_machine()
    print(str(process.states))
    print("result = " + str(test_result))
    print()
    print()
    print("+++ Testing CSP State Machine Class Built Directly +++")

    fdr.new_session()
    fdr.load_model("../sm-test/simple.csp")
    main_process = "a -> (b -> SKIP [] c -> SKIP)"
    config_file = "../sm-test/sm_test.yaml"
    state_machine = (fdr.convert_to_state_machine(main_process))
    print(str(state_machine.states))
    test_result = state_machine.test_machine()
    print("result = " + str(test_result))
