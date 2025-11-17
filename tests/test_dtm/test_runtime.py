"""Runtime behavior tests for deterministic Turing machines."""

import types

import automata.base.exceptions as exceptions
from automata.tm.dtm import DTM
from tests.test_dtm.base import DTMTestCase


class TestDTMRuntime(DTMTestCase):
    """Cover read_input flows, acceptance helpers, and custom machines."""

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable TM input is given."""
        final_config = self.dtm1.read_input("00001111")
        self.assertEqual(final_config.state, "q4")
        self.assertEqual(str(final_config.tape), "TMTape('xxxxyyyy..', '.', 9)")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dtm1.read_input_stepwise("00001111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        self.assertEqual(configs[0].state, "q0")
        self.assertEqual(str(configs[0].tape), "TMTape('00001111', '.', 0)")
        self.assertEqual(configs[-1].state, "q4")
        self.assertEqual(str(configs[-1].tape), "TMTape('xxxxyyyy..', '.', 9)")

    def test_read_input_offset(self) -> None:
        """Should valdiate input when tape is offset."""
        final_config = self.dtm2.read_input("01010101")
        self.assertEqual(final_config.state, "q4")
        self.assertEqual(str(final_config.tape), "TMTape('yyx1010101', '.', 3)")

    def test_read_input_rejection(self) -> None:
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.dtm1.read_input("000011")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.dtm1.read_input("02")

    def test_accepts_input_true(self) -> None:
        """Should return False if DTM input is not accepted."""
        self.assertTrue(self.dtm1.accepts_input("00001111"))

    def test_accepts_input_false(self) -> None:
        """Should return False if DTM input is rejected."""
        self.assertFalse(self.dtm1.accepts_input("000011"))

    def test_transition_without_movement(self) -> None:
        """Tests transitions without movements."""
        dtm = DTM(
            input_symbols={"0", "1", "2"},
            tape_symbols={"0", "1", "2", "*", "."},
            transitions={
                "q0": {
                    "0": ("q1", "*", "N"),
                    "*": ("q0", "*", "R"),
                    ".": ("qe", ".", "N"),
                },
                "q1": {
                    "0": ("q1", "0", "R"),
                    "1": ("q2", "*", "N"),
                    "*": ("q1", "*", "R"),
                },
                "q2": {
                    "1": ("q2", "1", "R"),
                    "2": ("q3", "*", "N"),
                    "*": ("q2", "*", "R"),
                },
                "q3": {
                    "2": ("q3", "2", "R"),
                    "*": ("q3", "*", "R"),
                    ".": ("q4", ".", "L"),
                },
                "q4": {
                    "0": ("q5", "0", "L"),
                    "1": ("q5", "1", "L"),
                    "2": ("q5", "2", "L"),
                    "*": ("q4", "*", "L"),
                    ".": ("qe", ".", "R"),
                },
                "q5": {
                    "0": ("q5", "0", "L"),
                    "1": ("q5", "1", "L"),
                    "2": ("q5", "2", "L"),
                    "*": ("q5", "*", "L"),
                    ".": ("q0", ".", "R"),
                },
            },
            states={"q0", "q1", "q2", "q3", "q4", "q5", "qe"},
            initial_state="q0",
            blank_symbol=".",
            final_states={"qe"},
        )
        self.assertTrue(dtm.accepts_input(""))
        self.assertTrue(dtm.accepts_input("012"))
        self.assertTrue(dtm.accepts_input("001122"))
        self.assertFalse(dtm.accepts_input("0"))
        self.assertFalse(dtm.accepts_input("01"))
        self.assertFalse(dtm.accepts_input("0112"))
        self.assertFalse(dtm.accepts_input("012012"))
