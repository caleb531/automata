"""Tests covering DFA construction and basic interactions."""

import types
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from tests.test_dfa.base import DfaTestCase


class TestDfaConstruction(DfaTestCase):
    """Verify DFA construction, immutability, and basic input handling."""

    def test_init_dfa(self) -> None:
        new_dfa = self.dfa.copy()
        self.assertIsNot(new_dfa, self.dfa)

    def test_init_dfa_missing_formal_params(self) -> None:
        with self.assertRaises(TypeError):
            DFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_copy_dfa(self) -> None:
        new_dfa = self.dfa.copy()
        self.assertIsNot(new_dfa, self.dfa)

    def test_dfa_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.dfa.states = {}  # type: ignore

    def test_dfa_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.dfa.states

    def test_dfa_immutable_dict(self) -> None:
        self.assertIsInstance(hash(frozendict(self.dfa.input_parameters)), int)

    @patch("automata.fa.dfa.DFA.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        self.dfa.copy()
        validate.assert_called_once_with()

    def test_dfa_equal(self) -> None:
        new_dfa = self.dfa.copy()
        self.assertTrue(self.dfa == new_dfa, "DFAs are not equal")

    def test_dfa_not_equal(self) -> None:
        new_dfa = DFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertTrue(self.dfa != new_dfa, "DFAs are equal")

    def test_validate_missing_state(self) -> None:
        with self.assertRaises(exceptions.MissingStateError):
            DFA(
                states={"q0", "q1"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_missing_symbol(self) -> None:
        with self.assertRaises(exceptions.MissingSymbolError):
            DFA(
                states={"q0"},
                input_symbols={"a", "b"},
                transitions={"q0": {"a": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_symbol(self) -> None:
        with self.assertRaises(exceptions.InvalidSymbolError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q0", "b": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q1",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={3},
            )

    def test_read_input_accepted(self) -> None:
        self.assertEqual(self.dfa.read_input("0111"), "q1")

    def test_read_input_rejection(self) -> None:
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input("011")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input("01112")

    def test_accepts_input_true(self) -> None:
        self.assertTrue(self.dfa.accepts_input("0111"))
        self.assertIn("0111", self.dfa)

    def test_accepts_input_false(self) -> None:
        self.assertFalse(self.dfa.accepts_input("011"))
        self.assertNotIn("011", self.dfa)
        self.assertNotIn(1, self.nfa)

    def test_read_input_step(self) -> None:
        validation_generator = self.dfa.read_input_stepwise("0111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(
            list(validation_generator),
            ["q0", "q0", "q1", "q2", "q1"],
        )

    def test_operations_other_types(self) -> None:
        other = 42
        self.assertNotEqual(self.dfa, other)
        with self.assertRaises(TypeError):
            self.dfa | other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa & other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa - other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa ^ other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa < other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa <= other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa > other  # type: ignore
        with self.assertRaises(TypeError):
            self.dfa >= other  # type: ignore

    def test_to_complete_trap_state_exception(self) -> None:
        with self.assertRaises(exceptions.InvalidStateError):
            self.partial_dfa.to_complete(0)

    def test_to_complete_no_extra_state(self) -> None:
        alphabet = ["d", "e", "g", "h", "i", "k", "o", "t", "x"]
        substring = "ti"
        dfa = DFA.from_prefix(set(alphabet), substring, contains=False)
        self.assertEqual(dfa.states, dfa.to_complete().states)
