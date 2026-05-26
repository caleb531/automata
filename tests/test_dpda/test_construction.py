"""Construction and validation checks for deterministic pushdown automata."""

from frozendict import frozendict

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
from automata.pda.dpda import DPDA
from tests.test_dpda.base import DPDATestCase


class TestDPDAConstruction(DPDATestCase):
    """Verify initialization semantics and structural validation."""

    def test_init_dpda(self) -> None:
        """Should copy DPDA if passed into DPDA constructor."""
        new_dpda = self.dpda.copy()
        self.assertIsNot(new_dpda, self.dpda)

    def test_init_dpda_missing_formal_params(self) -> None:
        """Should raise an error if formal DPDA parameters are missing."""
        with self.assertRaises(TypeError):
            DPDA(  # type: ignore
                states={"q0", "q1", "q2"},
                input_symbols={"a", "b"},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_init_dpda_no_acceptance_mode(self) -> None:
        """Should create a new DPDA."""
        new_dpda = DPDA(
            states={"q0"},
            input_symbols={"a", "b"},
            stack_symbols={"#"},
            transitions={"q0": {"a": {"#": ("q0", "")}}},
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q0"},
        )
        self.assertEqual(new_dpda.acceptance_mode, "both")

    def test_init_dpda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with self.assertRaises(pda_exceptions.InvalidAcceptanceModeError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
                acceptance_mode="foo",  # type: ignore
            )

    def test_dpda_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.dpda.states = set()

    def test_dpda_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.dpda.states

    def test_dpda_immutable_dict(self) -> None:
        """Should create a DPDA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.dpda.input_parameters)), int)

    def test_validate_invalid_input_symbol(self) -> None:
        """Should raise error if a transition has an invalid input symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {
                        "a": {"1": ("q1", ("1", "1"))},
                        "b": {"1": ("q2", "")},
                        "c": {"1": ("q2", "")},
                    },
                    "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {
                        "a": {"1": ("q1", ("1", "1")), "2": ("q1", ("1", "1"))},
                        "b": {"1": ("q2", "")},
                    },
                    "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_nondeterminism(self) -> None:
        """Should raise error if DPDA exhibits nondeterminism."""
        with self.assertRaises(pda_exceptions.NondeterminismError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                    "q2": {
                        "b": {"0": ("q2", "0"), "1": ("q2", "")},
                        "": {"0": ("q3", ("0",))},
                    },
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q1",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="2",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={1},
            )
