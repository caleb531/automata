"""Classes and functions for testing the behavior of MNTMs."""

import math
import random
import types
from typing import Set, cast
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.mntm import MNTM


class TestMNTM(test_tm.TestTM):
    """A test class for testing multitape nondeterministic Turing machines."""

    def test_init_mntm(self) -> None:
        """Should copy MNTM if passed into MNTM constructor."""
        new_mntm = self.mntm1.copy()
        self.assertIsNot(new_mntm, self.mntm1)

    def test_init_mntm_missing_formal_params(self) -> None:
        """Should raise an error if formal MNTM parameters are missing."""
        with self.assertRaises(TypeError):
            MNTM(  # type: ignore
                states={"q0", "q1", "q2", "q3", "q4"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "x", "y", "."},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q4"},
            )

    @patch("automata.tm.mntm.MNTM.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate MNTM when initialized."""
        self.mntm1.copy()
        validate.assert_called_once_with()

    def test_copy_ntm(self) -> None:
        """Should create exact copy of MNTM if copy() method is called."""
        new_mntm = self.mntm1.copy()
        self.assertIsNot(new_mntm, self.mntm1)

    def test_mntm_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.mntm1.states = set()

    def test_mntm_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.mntm1.states

    def test_mntm_immutable_dict(self) -> None:
        """Should create a DPDA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.mntm1.input_parameters)), int)

    def test_validate_input_symbol_subset(self) -> None:
        """Should raise error if input symbols are not a strict superset of tape
        symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_transition_state(self) -> None:
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q5": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_transition_symbol(self) -> None:
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("5", "#"): [("q1", (("#", "R"), ("#", "R")))],
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_transition_result_state(self) -> None:
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q5", (("#", "L"), ("#", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_transition_result_symbol(self) -> None:
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q1", ((".", "L"), ("#", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_transition_result_direction(self) -> None:
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q1", (("#", "U"), ("#", "R")))],  # type: ignore
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q5",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q1": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_nonfinal_initial_state(self) -> None:
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q0", "q1"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q5"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={5},
            )

    def test_validate_final_state_transitions(self) -> None:
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    },
                    "q1": {("0", "#"): [("q0", (("0", "L"), ("0", "R")))]},
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_tapes_consistency_too_few_specified(self) -> None:
        with self.assertRaises(tm_exceptions.InconsistentTapesException):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=3,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_validate_tapes_consistency_too_many_specified(self) -> None:
        with self.assertRaises(tm_exceptions.InconsistentTapesException):
            MNTM(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "#"},
                n_tapes=2,
                transitions={
                    "q0": {
                        ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
                        ("0", "#"): [("q0", (("0", "R"), ("#", "N"), ("#", "R")))],
                        ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
                    }
                },
                initial_state="q0",
                blank_symbol="#",
                final_states={"q1"},
            )

    def test_read_extended_tape(self) -> None:
        self.assertEqual(
            self.mntm1._read_extended_tape("10^10_1^00_00#^_", "^"), ("0", "1", "#")
        )
        self.assertEqual(
            self.mntm1._read_extended_tape("1.10_1.00_0.#_", "."), ("1", "1", "0")
        )
        self.assertEqual(
            self.mntm1._read_extended_tape("10#^_00#^_00^_", "^"), ("#", "#", "0")
        )

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "head symbol was found on leftmost " + "end of the extended tape",
        ):
            self.assertEqual(
                self.mntm1._read_extended_tape("^10#_1^010#_00^", "^"), ("", "1", "0")
            )

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "no head symbol found on one of the " + "virtual tapes",
        ):
            self.assertEqual(
                self.mntm1._read_extended_tape("0^10#_1010#_00^_", "^"), ("0", "", "0")
            )

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "there must be 1 virtual head for " + "every tape separator symbol",
        ):
            self.assertEqual(
                self.mntm1._read_extended_tape("0^1010^10#^", "^"), ("0", "0", "#")
            )

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "more than one head symbol found on " + "one of the virtual tapes",
        ):
            self.assertEqual(
                self.mntm1._read_extended_tape("0^101010^_#^_", "^"), ("0", "0", "#")
            )

    def test_read_input_as_ntm(self) -> None:
        validation_generator = self.mntm2.read_input_as_ntm("#0000")
        configs = list(validation_generator)
        first_config = set(configs[0]).pop()
        self.assertEqual(first_config.state, "q-1")
        self.assertEqual(str(first_config.tape), "TMTape('#^0000_#^_#^_', '#', 0)")
        last_config = set(configs[-1]).pop()
        self.assertEqual(last_config.state, "qf")
        self.assertEqual(
            str(last_config.tape), "TMTape('#0000#^_#0000#^_#XYYY#^_', '#', 23)"
        )

        # Test that it throws a RejectionException
        with self.assertRaises(exceptions.RejectionException):
            for _ in self.mntm2.read_input_as_ntm("#00"):
                pass

        # Thoroughly test the MNTM as an NTM and check that the final tapes are the same
        # regardless of whether the MNTM is run as an NTM or an MNTM
        mntms = [self.mntm1, self.mntm2, self.mntm3]
        inputs = ["0110", "#0000", "0101"]

        for mntm, input_str in zip(mntms, inputs):
            # Test that it doesn't throw a RejectionException
            self.assertTrue(mntm.accepts_input(input_str))
            configs = list(mntm.read_input_stepwise(input_str))
            final_mntm_config = cast(Set, configs[-1]).pop()

            # Test that the final tape of the MNTM is the same as the final tape of the
            # MNTM ran as an NTM.
            # First, join the tapes of the MNTM, as they would (and should) be in the
            # NTM version ^ being the head symbol, _ being the tape separator
            final_mntm_tape = ""
            for tape in final_mntm_config.tapes:
                curr_tape = "".join(tape.tape)

                # Add a ^ after the current position, for the head symbol
                curr_tape_pos = tape.current_position + 1

                # For self.mntm1 with input 0110, the final tape of the MNTM should be
                # 0110#^_11#^_ in the end as a result of concatenating:
                # MTMConfig... ('q1', (TMTape('0110#', '#', 4), TMTape('11#', '#', 2)))
                final_mntm_tape += (
                    curr_tape[:curr_tape_pos] + "^" + curr_tape[curr_tape_pos:] + "_"
                )

            # Now, run the MNTM as an NTM
            configs = list(mntm.read_input_as_ntm(input_str))
            final_ntm_config = cast(Set, configs[-1]).pop()

            # e.g., 0110#^_11#^_ for self.mntm1 with input 0110 as a result of:
            # TMConfiguration('q1', TMTape('0110#^_11#^_', '#', 11))
            final_ntm_tape = "".join(final_ntm_config.tape.tape)

            # Finally, assert that the final tapes are the same
            self.assertEqual(final_mntm_tape, final_ntm_tape)

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable TM input is given."""
        final_config = self.mntm1.read_input("0101101011").pop()
        self.assertEqual(final_config.state, "q1")
        self.assertEqual(str(final_config.tapes[0]), "TMTape('0101101011#', '#', 10)")
        self.assertEqual(str(final_config.tapes[1]), "TMTape('111111#', '#', 6)")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.mntm1.read_input_stepwise("0010101111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config.state, "q0")
        self.assertEqual(str(first_config.tapes[0]), "TMTape('0010101111', '#', 0)")
        self.assertEqual(str(first_config.tapes[1]), "TMTape('#', '#', 0)")
        last_config = configs[-1].pop()
        self.assertEqual(last_config.state, "q1")
        self.assertEqual(str(last_config.tapes[0]), "TMTape('0010101111#', '#', 10)")
        self.assertEqual(str(last_config.tapes[1]), "TMTape('111111#', '#', 6)")

    def test_read_input_rejection(self) -> None:
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.mntm1.read_input("2")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.mntm2.read_input("1")

    def test_accepts_input_true(self) -> None:
        """Should return False if MNTM input is not accepted."""
        test_limit = 20
        for i in range(test_limit):
            input_str_1 = ""
            input_str_2 = "#0"
            input_str_3 = "1"
            for _ in range(i):
                k = random.randint(0, 1)
                input_str_1 += str(k)
                input_str_2 += "0"
                input_str_3 += str(k)

            input_str_3 += input_str_3
            # Should accept all
            self.assertTrue(self.mntm1.accepts_input(input_str_1))
            self.assertTrue(self.mntm3.accepts_input(input_str_3))

            # Should not accept because this would not be of the form ww
            self.assertFalse(
                self.mntm3.accepts_input(input_str_3 + str(random.randint(0, 1)))
            )

            # Should accept only if input string's length is a perfect square
            if self.is_perfect_square(len(input_str_2) - 1):
                self.assertTrue(self.mntm2.accepts_input(input_str_2))
            else:
                self.assertFalse(self.mntm2.accepts_input(input_str_2))

    def test_accepts_input_false(self) -> None:
        """Should return False if MNTM input is rejected."""
        self.assertFalse(self.mntm1.accepts_input("000012"))
        self.assertFalse(self.mntm2.accepts_input("#00000"))

    @staticmethod
    def is_perfect_square(number: int) -> bool:
        return number == int(math.sqrt(number)) ** 2
