"""Runtime behavior tests for nondeterministic Turing machines."""

import types

import automata.base.exceptions as exceptions
from tests.test_ntm.base import NTMTestCase


class TestNTMRuntime(NTMTestCase):
    """Cover read_input flows and acceptance helpers for NTMs."""

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable TM input is given."""
        final_config = self.ntm1.read_input("00120001111").pop()
        self.assertEqual(final_config.state, "q3")
        self.assertEqual(str(final_config.tape), "TMTape('00120001111.', '.', 11)")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.ntm1.read_input_stepwise("00120001111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config.state, "q0")
        self.assertEqual(str(first_config.tape), "TMTape('00120001111', '.', 0)")
        last_config = configs[-1].pop()
        self.assertEqual(last_config.state, "q3")
        self.assertEqual(str(last_config.tape), "TMTape('00120001111.', '.', 11)")

    def test_read_input_rejection(self) -> None:
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.ntm1.read_input("0")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.ntm1.read_input("02")

    def test_accepts_input_true(self) -> None:
        """Should return True if NTM input is accepted."""
        self.assertTrue(self.ntm1.accepts_input("00001111"))

    def test_accepts_input_false(self) -> None:
        """Should return False if NTM input is rejected."""
        self.assertFalse(self.ntm1.accepts_input("3"))
