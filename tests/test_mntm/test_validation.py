"""Validation error handling for multitape NTM definitions."""

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
from automata.tm.mntm import MNTM
from tests.test_mntm.base import MNTMTestCase


class TestMNTMValidation(MNTMTestCase):
    """Exercise structural validation around MNTM definitions."""

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
        """Should raise error when fewer transition tapes are provided than expected."""
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
        """Should raise error when more transition tapes are provided than expected."""
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
