"""Acceptance and execution behavior for deterministic pushdown automata."""

import automata.base.exceptions as exceptions
from automata.pda.configuration import PDAConfiguration
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack
from tests.test_dpda.base import DPDATestCase


class TestDPDAAcceptance(DPDATestCase):
    """Ensure DPDAs process input according to their acceptance mode."""

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if DPDA accepts by final state."""
        config = self.dpda.read_input("aabb")
        self.assertEqual(config, PDAConfiguration("q3", "", PDAStack(["0"])))

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
        config = dpda.read_input("aabb")
        self.assertEqual(config, PDAConfiguration("q2", "", PDAStack([])))

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
        config = dpda.read_input("aabb")
        self.assertEqual(config, PDAConfiguration("q4", "", PDAStack(["0"])))

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
        """Should return True if DPDA input is accepted."""
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
            transitions={},
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q0"},
            acceptance_mode="both",
        )
        self.assertTrue(dpda.accepts_input(""))
