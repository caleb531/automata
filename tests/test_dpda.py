#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

from frozendict import frozendict

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack


class TestDPDA(test_pda.TestPDA):
    """A test class for testing deterministic finite automata."""

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

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if DPDA accepts by final state."""
        self.assertEqual(
            self.dpda.read_input("aabb"), PDAConfiguration("q3", "", PDAStack(["0"]))
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="empty_stack",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aabb")

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="empty_stack",
        )
        self.assertEqual(
            dpda.read_input("aabb"), PDAConfiguration("q2", "", PDAStack([]))
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if DPDA accepts by final state."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aabb")

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                "q3": {"": {"0": ("q4", ("0",))}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q4"},
            acceptance_mode="final_state",
        )
        self.assertEqual(
            dpda.read_input("aabb"), PDAConfiguration("q4", "", PDAStack(["0"]))
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if DPDA accepts by final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input("aab")

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aab")

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input("01")

    def test_accepts_input_true(self) -> None:
        """Should return False if DPDA input is not accepted."""
        self.assertTrue(self.dpda.accepts_input("aabb"))

    def test_accepts_input_false(self) -> None:
        """Should return False if DPDA input is rejected."""
        self.assertFalse(self.dpda.accepts_input("aab"))

    def test_empty_dpda(self) -> None:
        """Should accept an empty input if the DPDA is empty."""
        dpda = DPDA(
            states={"q0"},
            input_symbols=set(),
            stack_symbols={"0"},
            transitions=dict(),
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q0"},
            acceptance_mode="both",
        )
        self.assertTrue(dpda.accepts_input(""))
