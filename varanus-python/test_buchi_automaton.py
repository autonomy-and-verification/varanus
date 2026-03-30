import unittest

from csp_state_machine import CSPStateMachine, Transition


class BuchiAutomatonExportTests(unittest.TestCase):

    def test_visible_transitions_are_total_bdd_cubes(self):
        machine = CSPStateMachine()
        for state_name in ("0", "1", "2", "3"):
            machine.add_state(state_name)

        machine.add_transition_by_name("a", "0", "1")
        machine.add_transition_by_name("b", "1", "2")
        machine.add_transition_by_name(Transition._TERMINATE, "2", "3")
        machine.alphabet = set(["a", "b"])
        machine.initial_state = machine.states["0"]
        machine.current_state = machine.initial_state

        hoa = machine.to_buchi_automaton().splitlines()

        self.assertIn("[0 & !1] 1", hoa)
        self.assertIn("[!0 & 1] 2", hoa)
        self.assertIn("[!0 & !1] 3", hoa)
        self.assertIn("State: 3 {0}", hoa)
        self.assertIn("[true] 3", hoa)


if __name__ == "__main__":
    unittest.main()
