"""Construction and validation tests for NFAs."""

import types
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
from automata.fa.nfa import NFA
from tests.test_nfa.base import NFATestCase


class TestNFAConstruction(NFATestCase):
    """Verify NFA construction, validation, and basic input handling."""

    def test_init_nfa(self) -> None:
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self) -> None:
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            NFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_copy_nfa(self) -> None:
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_nfa_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.nfa.states = {}  # type: ignore

    def test_nfa_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.nfa.states

    def test_nfa_immutable_dict(self) -> None:
        """Should create an NFA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.nfa.input_parameters)), int)

    def test_init_dfa(self) -> None:
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA.from_dfa(self.dfa)
        self.assertEqual(nfa.states, {"q0", "q1", "q2"})
        self.assertEqual(nfa.input_symbols, {"0", "1"})
        self.assertEqual(
            nfa.transitions,
            {
                "q0": {"0": {"q0"}, "1": {"q1"}},
                "q1": {"0": {"q0"}, "1": {"q2"}},
                "q2": {"0": {"q2"}, "1": {"q1"}},
            },
        )
        self.assertEqual(nfa.initial_state, "q0")

    @patch("automata.fa.nfa.NFA.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate NFA when initialized."""
        self.nfa.copy()
        validate.assert_called_once_with()

    def test_nfa_equal(self) -> None:
        """Should correctly determine if two NFAs are equal."""
        nfa1 = NFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"": {"q1"}},
                "q1": {"a": {"q2"}},
                "q2": {"a": {"q2"}, "": {"q3"}},
                "q3": {"b": {"q1"}},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        nfa2 = NFA(
            states={0, 1, 2, 3},
            input_symbols={"a", "b"},
            transitions={
                0: {"": {1}},
                1: {"a": {2}},
                2: {"a": {2}, "": {3}},
                3: {"b": {1}},
            },
            initial_state=0,
            final_states={3},
        )
        self.assertEqual(nfa1, nfa2)
        self.assertEqual(nfa1.eliminate_lambda(), nfa2.eliminate_lambda())

    def test_nfa_not_equal(self) -> None:
        """Should correctly determine if two NFAs are not equal."""
        nfa1 = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": {"q1"}},
                "q1": {"a": {"q1"}, "": {"q2"}},
                "q2": {"b": {"q0"}},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        nfa2 = NFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": {"q0"}}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertNotEqual(nfa1, nfa2)

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"b": {"q0"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q1"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q1",
                final_states={"q0"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            NFA(
                states={"q0", "q1"},
                input_symbols={"a"},
                transitions={},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q0",
                final_states={3},
            )
            self.nfa.validate()

    def test_read_input_accepted(self) -> None:
        """Should return correct states if acceptable NFA input is given."""
        self.assertEqual(self.nfa.read_input("aba"), {"q1", "q2"})

    def test_validate_missing_state(self) -> None:
        """Should silently ignore states without transitions defined."""
        NFA(
            states={"q0"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": {"q0"}}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertIsNotNone(self.nfa.transitions)

    def test_read_input_rejection(self) -> None:
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abba")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abc")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise("aba")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(
            list(validation_generator),
            [{"q0"}, {"q1", "q2"}, {"q0"}, {"q1", "q2"}],
        )

    def test_accepts_input_true(self) -> None:
        """Should return True if NFA input is accepted."""
        self.assertTrue(self.nfa.accepts_input("aba"))
        self.assertIn("aba", self.nfa)

    def test_accepts_input_false(self) -> None:
        """Should return False if NFA input is rejected."""
        self.assertFalse(self.nfa.accepts_input("abba"))
        self.assertNotIn("abba", self.nfa)
        self.assertNotIn(1, self.nfa)

    def test_cyclic_lambda_transitions(self) -> None:
        """Should traverse NFA containing cyclic lambda transitions."""
        nfa = NFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a"},
            transitions={
                "q0": {"": {"q1", "q3"}},
                "q1": {"a": {"q2"}},
                "q2": {"": {"q3"}},
                "q3": {"": {"q0"}},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        self.assertEqual(nfa.read_input(""), {"q0", "q1", "q3"})
        self.assertEqual(nfa.read_input("a"), {"q0", "q1", "q2", "q3"})

    def test_non_str_states(self) -> None:
        """Should handle non-string state names"""
        nfa = NFA(
            states={0},
            input_symbols={"0"},
            transitions={0: {}},
            initial_state=0,
            final_states=set(),
        )
        self.assertIsNotNone(nfa.accepts_input(""))
