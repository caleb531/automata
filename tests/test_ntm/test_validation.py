"""Validation-focused tests for nondeterministic Turing machines."""

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
from automata.tm.ntm import NTM
from tests.test_ntm.base import NTMTestCase


class TestNTMValidation(NTMTestCase):
    """Exercise validation logic for NTM configuration errors."""

    def test_validate_input_symbol_subset(self) -> None:
        """Should raise error if input symbols are not a strict superset of tape
        symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0"},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_state(self) -> None:
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                    "q4": {"0": {("q1", "0", "R")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_symbol(self) -> None:
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}, "3": {("q0", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_state(self) -> None:
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}, ".": {("q4", ".", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_symbol(self) -> None:
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}, ".": {("q2", "5", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_transition_result_direction(self) -> None:
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "U")}},  # type: ignore
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q5",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={"q1": {"0": {("q2", "0", "L")}}},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )

    def test_validate_nonfinal_initial_state(self) -> None:
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q5"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={5},
            )

    def test_validate_final_state_transitions(self) -> None:
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            NTM(
                states={"q0", "q1", "q2"},
                input_symbols={"0"},
                tape_symbols={"0", "."},
                transitions={
                    "q0": {"0": {("q1", "0", "R")}},
                    "q1": {"0": {("q2", "0", "L")}},
                    "q2": {"0": {("q1", "0", "L")}},
                },
                initial_state="q0",
                blank_symbol=".",
                final_states={"q2"},
            )
