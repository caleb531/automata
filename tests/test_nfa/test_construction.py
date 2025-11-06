"""Construction and validation tests for NFAs."""

import types
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
from automata.fa.nfa import NFA
from tests.test_nfa.base import NfaTestCase


class TestNfaConstruction(NfaTestCase):
    """Verify NFA construction, validation, and basic input handling."""

    def test_init_nfa(self) -> None:
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self) -> None:
        with self.assertRaises(TypeError):
            NFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_copy_nfa(self) -> None:
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_nfa_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.nfa.states = {}  # type: ignore

    def test_nfa_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.nfa.states

    def test_nfa_immutable_dict(self) -> None:
        self.assertIsInstance(hash(frozendict(self.nfa.input_parameters)), int)

    def test_init_dfa(self) -> None:
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
        self.nfa.copy()
        validate.assert_called_once_with()

    def test_nfa_equal(self) -> None:
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
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"b": {"q0"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q1"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q1",
                final_states={"q0"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        with self.assertRaises(exceptions.MissingStateError):
            NFA(
                states={"q0", "q1"},
                input_symbols={"a"},
                transitions={},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
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
        self.assertEqual(self.nfa.read_input("aba"), {"q1", "q2"})

    def test_validate_missing_state(self) -> None:
        NFA(
            states={"q0"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": {"q0"}}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertIsNotNone(self.nfa.transitions)

    def test_read_input_rejection(self) -> None:
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abba")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abc")

    def test_read_input_step(self) -> None:
        validation_generator = self.nfa.read_input_stepwise("aba")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(
            list(validation_generator),
            [{"q0"}, {"q1", "q2"}, {"q0"}, {"q1", "q2"}],
        )

    def test_accepts_input_true(self) -> None:
        self.assertTrue(self.nfa.accepts_input("aba"))
        self.assertIn("aba", self.nfa)

    def test_accepts_input_false(self) -> None:
        self.assertFalse(self.nfa.accepts_input("abba"))
        self.assertNotIn("abba", self.nfa)
        self.assertNotIn(1, self.nfa)

    def test_cyclic_lambda_transitions(self) -> None:
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
        nfa = NFA(
            states={0},
            input_symbols={"0"},
            transitions={0: {}},
            initial_state=0,
            final_states=set(),
        )
        self.assertIsNotNone(nfa.accepts_input(""))


__all__ = ["TestNfaConstruction"]
