"""Acceptance semantics and input-processing tests for NPDAs."""

import automata.base.exceptions as exceptions
from automata.pda.configuration import PDAConfiguration
from automata.pda.npda import NPDA
from automata.pda.stack import PDAStack
from tests.test_npda.base import NPDATestCase


class TestNPDAAcceptance(NPDATestCase):
    """Cover acceptance modes, read_input behavior, and helpers."""

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if NPDA accepts by final state."""
        self.assertEqual(
            self.npda.read_input("abaaba"),
            {PDAConfiguration("q2", "", PDAStack(["#"]))},
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q2"},
            acceptance_mode="empty_stack",
        )
        with self.assertRaises(exceptions.RejectionException):
            npda.read_input("abaaba")

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q2", "")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states=set(),
            acceptance_mode="empty_stack",
        )
        self.assertEqual(
            npda.read_input("abaaba"), {PDAConfiguration("q2", "", PDAStack([]))}
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if NPDA accepts by final state."""
        npda = NPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q3", "")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q2"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            npda.read_input("abaaba")

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        npda = NPDA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q3", "#")}}},
                "q3": {"": {"#": {("q4", "#")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q4"},
            acceptance_mode="final_state",
        )
        self.assertEqual(
            npda.read_input("abaaba"), {PDAConfiguration("q4", "", PDAStack(["#"]))}
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if NPDA accepts by final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.npda.read_input("aaba")

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q2", "")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states=set(),
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            npda.read_input("aaba")

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with self.assertRaises(exceptions.RejectionException):
            self.npda.read_input("01")

    def test_accepts_input_true(self) -> None:
        """Should return True if NPDA input is accepted."""
        self.assertTrue(self.npda.accepts_input("abaaba"))

    def test_accepts_input_false(self) -> None:
        """Should return False if NPDA input is rejected."""
        self.assertFalse(self.npda.accepts_input("aaba"))
