"""Validation error handling for deterministic Turing machines."""

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
from automata.tm.dtm import DTM
from tests.test_dtm.base import DTMTestCase


class TestDTMValidation(DTMTestCase):
    """Exercise structural validation for DTM definitions."""

    def test_validate_input_symbol_subset(self) -> None:
        """Should raise error when input symbols omit tape symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0"},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q2", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_state(self) -> None:
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q5": {"0": ("q2", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_symbol(self) -> None:
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"5": ("q0", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_state(self) -> None:
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q5", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_symbol(self) -> None:
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "5", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_direction(self) -> None:
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "U")},  # type: ignore
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q5",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={"q1": {"0": ("q0", "0", "L")}},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q5"},
            )

    def test_validate_nonfinal_initial_state(self) -> None:
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q5"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={2},
            )

    def test_validate_final_state_transitions(self) -> None:
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                    "q2": {"0": ("q1", "0", "R")},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_blank_symbol(self) -> None:
        """Should raise an error if the blank symbol is not valid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": ("q1", "0", "R")},
                    "q1": {"0": ("q0", "0", "L")},
                },
                initial_state="q0",
                blank_symbol="_",
                final_states={"q2"},
            )
