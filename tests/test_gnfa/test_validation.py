"""Validation error handling for GNFA definitions."""

import automata.base.exceptions as exceptions
from automata.fa.gnfa import GNFA
from tests.test_gnfa.base import GNFATestCase


class TestGNFAValidation(GNFATestCase):
    """Exercise structural validation rules for GNFAs."""

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidRegexError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "c", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {
                        "q3": "a",
                        "q1": "a",
                        "q_f": None,
                        "q2": None,
                        "q0": None,
                    },
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q3",
                final_state="q_f",
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q3",
            )

    def test_validate_final_state_transition(self) -> None:
        """Should raise error if there are transitions from final state"""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                    "q_f": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_missing_state(self) -> None:
        """Should raise an error if some transitions are missing."""
        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_incomplete_transitions(self) -> None:
        """Should raise error if transitions from (except final state)
        and to (except initial state) every state is missing."""
        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": ""},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {
                        "q0": "",
                        "q_f": None,
                        "q2": None,
                        "q1": None,
                        "q5": {},  # type: ignore
                    },
                },
                initial_state="q_in",
                final_state="q_f",
            )
