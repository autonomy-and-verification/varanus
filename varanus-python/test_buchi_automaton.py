import unittest

from csp_state_machine import CSPStateMachine, Transition


class BuchiAutomatonExportTests(unittest.TestCase):

    def test_visible_transitions_are_total_bdd_cubes_and_tick_is_reserved_for_stutter(self):
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

        # AP includes dedicated stutter atom.
        self.assertIn('AP: 3 "a" "b" "tick"', hoa)

        # Visible events force !tick.
        self.assertIn("[0 & !1 & !2] 1", hoa)
        self.assertIn("[!0 & 1 & !2] 2", hoa)

        # Termination is unobservable: no synthetic all-false edge for ✓.
        self.assertNotIn("[!0 & !1 & !2] 3", hoa)

        # Accepting states stutter only via tick.
        self.assertIn("State: 2 {0}", hoa)
        self.assertIn("State: 3 {0}", hoa)
        self.assertIn("[!0 & !1 & 2] 2", hoa)
        self.assertIn("[!0 & !1 & 2] 3", hoa)

    def test_deadlock_fallback_uses_tick_stutter(self):
        machine = CSPStateMachine()
        for state_name in ("0", "1"):
            machine.add_state(state_name)

        machine.add_transition_by_name("a", "0", "1")
        machine.alphabet = set(["a"])
        machine.initial_state = machine.states["0"]
        machine.current_state = machine.initial_state

        hoa = machine.to_buchi_automaton().splitlines()

        self.assertIn('AP: 2 "a" "tick"', hoa)
        self.assertIn("State: 1 {0}", hoa)
        self.assertIn("[!0 & 1] 1", hoa)


if __name__ == "__main__":
    unittest.main()
