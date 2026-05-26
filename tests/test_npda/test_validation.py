"""Validation error handling for NPDA definitions."""

import automata.base.exceptions as exceptions
from automata.pda.npda import NPDA
from tests.test_npda.base import NPDATestCase


class TestNPDAValidation(NPDATestCase):
    """Exercise structural validation around NPDA definitions."""

    def test_validate_invalid_input_symbol(self) -> None:
        """Should raise error if a transition has an invalid input symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"c": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"@": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="@",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={1},
            )
