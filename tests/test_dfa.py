#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import os
import os.path
import random
import tempfile
import types
from itertools import product
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestDFA(test_fa.TestFA):
    """A test class for testing deterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_dfa(self) -> None:
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = self.dfa.copy()
        self.assertIsNot(new_dfa, self.dfa)

    def test_init_dfa_missing_formal_params(self) -> None:
        """Should raise an error if formal DFA parameters are missing."""
        with self.assertRaises(TypeError):
            DFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_copy_dfa(self) -> None:
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assertIsNot(new_dfa, self.dfa)

    def test_dfa_immutable_attr_set(self) -> None:
        """Should disallow reassigning DFA attributes"""
        with self.assertRaises(AttributeError):
            self.dfa.states = {}  # type: ignore

    def test_dfa_immutable_attr_del(self) -> None:
        """Should disallow deleting DFA attributes"""
        with self.assertRaises(AttributeError):
            del self.dfa.states

    def test_dfa_immutable_dict(self) -> None:
        """Should create a DFA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.dfa.input_parameters)), int)

    @patch("automata.fa.dfa.DFA.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate DFA when initialized."""
        self.dfa.copy()
        validate.assert_called_once_with()

    def test_dfa_equal(self) -> None:
        """Should correctly determine if two DFAs are equal."""
        new_dfa = self.dfa.copy()
        self.assertTrue(self.dfa == new_dfa, "DFAs are not equal")

    def test_dfa_not_equal(self) -> None:
        """Should correctly determine if two DFAs are not equal."""
        new_dfa = DFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertTrue(self.dfa != new_dfa, "DFAs are equal")

    def test_validate_missing_state(self) -> None:
        """Should raise error if a state has no transitions defined."""
        with self.assertRaises(exceptions.MissingStateError):
            DFA(
                states={"q0", "q1"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_missing_symbol(self) -> None:
        """Should raise error if a symbol transition is missing."""
        with self.assertRaises(exceptions.MissingSymbolError):
            DFA(
                states={"q0"},
                input_symbols={"a", "b"},
                transitions={"q0": {"a": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q0", "b": "q0"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q1",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": "q1"}},
                initial_state="q0",
                final_states={3},
            )

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable DFA input is given."""
        self.assertEqual(self.dfa.read_input("0111"), "q1")

    def test_read_input_rejection(self) -> None:
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input("011")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input("01112")

    def test_accepts_input_true(self) -> None:
        """Should return True if DFA input is accepted."""
        self.assertTrue(self.dfa.accepts_input("0111"))

    def test_accepts_input_false(self) -> None:
        """Should return False if DFA input is rejected."""
        self.assertFalse(self.dfa.accepts_input("011"))

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dfa.read_input_stepwise("0111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(list(validation_generator), ["q0", "q0", "q1", "q2", "q1"])

    def test_operations_other_types(self) -> None:
        """Should raise TypeError for all but equals."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        other = 42
        self.assertNotEqual(dfa, other)
        with self.assertRaises(TypeError):
            dfa | other  # type: ignore
        with self.assertRaises(TypeError):
            dfa & other  # type: ignore
        with self.assertRaises(TypeError):
            dfa - other  # type: ignore
        with self.assertRaises(TypeError):
            dfa ^ other  # type: ignore
        with self.assertRaises(TypeError):
            dfa < other  # type: ignore
        with self.assertRaises(TypeError):
            dfa <= other  # type: ignore
        with self.assertRaises(TypeError):
            dfa > other  # type: ignore
        with self.assertRaises(TypeError):
            dfa >= other  # type: ignore

    def test_equivalence_not_equal(self) -> None:
        """Should not be equal."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        self.assertNotEqual(no_consecutive_11_dfa, zero_or_one_1_dfa)

    def test_equivalence_minify(self) -> None:
        """Should be equivalent after minify."""
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q3", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
                "q3": {"0": "q0", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q0", "q1", "q3"},
        )
        minimal_dfa = no_consecutive_11_dfa.minify()
        self.assertEqual(no_consecutive_11_dfa, minimal_dfa)

    def test_equivalence_two_non_minimal(self) -> None:
        """Should be equivalent even though they are non minimal."""
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q3", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
                "q3": {"0": "q0", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q0", "q1", "q3"},
        )
        other_dfa = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q3", "1": "q2"},
                "q3": {"0": "q3", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        self.assertEqual(no_consecutive_11_dfa, other_dfa)

    def test_complement(self) -> None:
        """Should compute the complement of a DFA"""
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        complement_dfa = no_consecutive_11_dfa.complement(
            retain_names=True, minify=False
        )
        self.assertEqual(complement_dfa.states, no_consecutive_11_dfa.states)
        self.assertEqual(
            complement_dfa.input_symbols, no_consecutive_11_dfa.input_symbols
        )
        self.assertEqual(complement_dfa.transitions, no_consecutive_11_dfa.transitions)
        self.assertEqual(
            complement_dfa.initial_state, no_consecutive_11_dfa.initial_state
        )
        self.assertEqual(complement_dfa.final_states, {"q2"})

    def test_union(self) -> None:
        """Should compute the union between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa2 = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        new_dfa = dfa1.union(dfa2, retain_names=True, minify=False)
        self.assertEqual(
            new_dfa.states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q2", "p2"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q3", "p2"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.transitions,
            {
                ("q0", "p0"): {"0": ("q0", "p0"), "1": ("q1", "p1")},
                ("q1", "p0"): {"0": ("q1", "p0"), "1": ("q2", "p1")},
                ("q1", "p1"): {"0": ("q1", "p0"), "1": ("q2", "p2")},
                ("q2", "p0"): {"0": ("q2", "p0"), "1": ("q3", "p1")},
                ("q2", "p1"): {"0": ("q2", "p0"), "1": ("q3", "p2")},
                ("q2", "p2"): {"0": ("q2", "p2"), "1": ("q3", "p2")},
                ("q3", "p0"): {"0": ("q3", "p0"), "1": ("q4", "p1")},
                ("q3", "p1"): {"0": ("q3", "p0"), "1": ("q4", "p2")},
                ("q3", "p2"): {"0": ("q3", "p2"), "1": ("q4", "p2")},
                ("q4", "p0"): {"0": ("q4", "p0"), "1": ("q4", "p1")},
                ("q4", "p1"): {"0": ("q4", "p0"), "1": ("q4", "p2")},
                ("q4", "p2"): {"0": ("q4", "p2"), "1": ("q4", "p2")},
            },
        )
        self.assertEqual(new_dfa.initial_state, ("q0", "p0"))
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )

        # Test retain names logic without minify
        self.assertEqual(dfa1.union(dfa2, retain_names=False, minify=False), new_dfa)

    def test_intersection(self) -> None:
        """Should compute the intersection between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa2 = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        new_dfa = dfa1.intersection(dfa2, retain_names=True, minify=False)
        self.assertEqual(
            new_dfa.states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q2", "p2"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q3", "p2"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.transitions,
            {
                ("q0", "p0"): {"0": ("q0", "p0"), "1": ("q1", "p1")},
                ("q1", "p0"): {"0": ("q1", "p0"), "1": ("q2", "p1")},
                ("q1", "p1"): {"0": ("q1", "p0"), "1": ("q2", "p2")},
                ("q2", "p0"): {"0": ("q2", "p0"), "1": ("q3", "p1")},
                ("q2", "p1"): {"0": ("q2", "p0"), "1": ("q3", "p2")},
                ("q2", "p2"): {"0": ("q2", "p2"), "1": ("q3", "p2")},
                ("q3", "p0"): {"0": ("q3", "p0"), "1": ("q4", "p1")},
                ("q3", "p1"): {"0": ("q3", "p0"), "1": ("q4", "p2")},
                ("q3", "p2"): {"0": ("q3", "p2"), "1": ("q4", "p2")},
                ("q4", "p0"): {"0": ("q4", "p0"), "1": ("q4", "p1")},
                ("q4", "p1"): {"0": ("q4", "p0"), "1": ("q4", "p2")},
                ("q4", "p2"): {"0": ("q4", "p2"), "1": ("q4", "p2")},
            },
        )
        self.assertEqual(new_dfa.initial_state, ("q0", "p0"))
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q4", "p0"),
                ("q4", "p1"),
            },
        )

        # Test retain names logic without minify
        self.assertEqual(
            dfa1.intersection(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_difference(self) -> None:
        """Should compute the difference between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa2 = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        new_dfa = dfa1.difference(dfa2, retain_names=True, minify=False)
        self.assertEqual(
            new_dfa.states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q2", "p2"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q3", "p2"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.transitions,
            {
                ("q0", "p0"): {"0": ("q0", "p0"), "1": ("q1", "p1")},
                ("q1", "p0"): {"0": ("q1", "p0"), "1": ("q2", "p1")},
                ("q1", "p1"): {"0": ("q1", "p0"), "1": ("q2", "p2")},
                ("q2", "p0"): {"0": ("q2", "p0"), "1": ("q3", "p1")},
                ("q2", "p1"): {"0": ("q2", "p0"), "1": ("q3", "p2")},
                ("q2", "p2"): {"0": ("q2", "p2"), "1": ("q3", "p2")},
                ("q3", "p0"): {"0": ("q3", "p0"), "1": ("q4", "p1")},
                ("q3", "p1"): {"0": ("q3", "p0"), "1": ("q4", "p2")},
                ("q3", "p2"): {"0": ("q3", "p2"), "1": ("q4", "p2")},
                ("q4", "p0"): {"0": ("q4", "p0"), "1": ("q4", "p1")},
                ("q4", "p1"): {"0": ("q4", "p0"), "1": ("q4", "p2")},
                ("q4", "p2"): {"0": ("q4", "p2"), "1": ("q4", "p2")},
            },
        )
        self.assertEqual(new_dfa.initial_state, ("q0", "p0"))
        self.assertEqual(new_dfa.final_states, {("q4", "p2")})

        # Test retain names logic without minify
        self.assertEqual(
            dfa1.difference(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_symmetric_difference(self) -> None:
        """Should compute the symmetric difference between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa2 = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        new_dfa = dfa1.symmetric_difference(dfa2, retain_names=True, minify=False)
        self.assertEqual(
            new_dfa.states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q2", "p2"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q3", "p2"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.transitions,
            {
                ("q0", "p0"): {"0": ("q0", "p0"), "1": ("q1", "p1")},
                ("q1", "p0"): {"0": ("q1", "p0"), "1": ("q2", "p1")},
                ("q1", "p1"): {"0": ("q1", "p0"), "1": ("q2", "p2")},
                ("q2", "p0"): {"0": ("q2", "p0"), "1": ("q3", "p1")},
                ("q2", "p1"): {"0": ("q2", "p0"), "1": ("q3", "p2")},
                ("q2", "p2"): {"0": ("q2", "p2"), "1": ("q3", "p2")},
                ("q3", "p0"): {"0": ("q3", "p0"), "1": ("q4", "p1")},
                ("q3", "p1"): {"0": ("q3", "p0"), "1": ("q4", "p2")},
                ("q3", "p2"): {"0": ("q3", "p2"), "1": ("q4", "p2")},
                ("q4", "p0"): {"0": ("q4", "p0"), "1": ("q4", "p1")},
                ("q4", "p1"): {"0": ("q4", "p0"), "1": ("q4", "p2")},
                ("q4", "p2"): {"0": ("q4", "p2"), "1": ("q4", "p2")},
            },
        )
        self.assertEqual(new_dfa.initial_state, ("q0", "p0"))
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q4", "p2"),
            },
        )

        # Test retain names logic without minify
        self.assertEqual(
            dfa1.symmetric_difference(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_issubset(self) -> None:
        """Should test if one DFA is a subset of another"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # Test both proper subset and subset with each set as left hand side
        self.assertTrue(zero_or_one_1_dfa < no_consecutive_11_dfa)
        self.assertTrue(zero_or_one_1_dfa <= no_consecutive_11_dfa)
        self.assertFalse(no_consecutive_11_dfa < zero_or_one_1_dfa)
        self.assertFalse(no_consecutive_11_dfa <= zero_or_one_1_dfa)

    def test_issuperset(self) -> None:
        """Should test if one DFA is a superset of another"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # Test both proper subset and subset with each set as left hand side
        self.assertFalse(zero_or_one_1_dfa > no_consecutive_11_dfa)
        self.assertFalse(zero_or_one_1_dfa >= no_consecutive_11_dfa)
        self.assertTrue(no_consecutive_11_dfa > zero_or_one_1_dfa)
        self.assertTrue(no_consecutive_11_dfa >= zero_or_one_1_dfa)

    def test_symbol_mismatch(self) -> None:
        """Should test if symbol mismatch is raised"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of b
        zero_or_one_b_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": "q0", "b": "q1"},
                "q1": {"a": "q1", "b": "q2"},
                "q2": {"a": "q2", "b": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.issubset(no_consecutive_11_dfa)

        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.difference(no_consecutive_11_dfa)

    def test_isdisjoint(self) -> None:
        """Should test if two DFAs are disjoint"""
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        input_symbols = {"0", "1"}
        at_least_three_1 = DFA.from_subsequence(input_symbols, "111")
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        at_most_one_1 = DFA(
            states={"q0", "q1", "q2"},
            input_symbols=input_symbols,
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA accepts all words which contain at least
        # one occurrence of 1
        at_least_one_1 = DFA.from_subsequence(input_symbols, "1")
        self.assertTrue(at_least_three_1.isdisjoint(at_most_one_1))
        self.assertTrue(at_most_one_1.isdisjoint(at_least_three_1))
        self.assertFalse(at_least_three_1.isdisjoint(at_least_one_1))
        self.assertFalse(at_most_one_1.isdisjoint(at_least_one_1))

    def test_isempty_non_empty(self) -> None:
        """Should test if a non-empty DFA is empty"""
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        dfa = DFA.from_subsequence({"0", "1"}, "111")
        self.assertFalse(dfa.isempty())

    def test_isempty_empty(self) -> None:
        """Should test if an empty DFA is empty"""
        # This DFA has no reachable final states and
        # therefore accepts the empty language
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q0", "1": "q1"},
                "q3": {"0": "q2", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        self.assertTrue(dfa1.isempty())

    def test_isfinite_infinite(self) -> None:
        """Should test if an infinite DFA is finite (case #1)"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa = DFA.from_substring({"0", "1"}, "11").complement(minify=False)
        self.assertFalse(dfa.isfinite())

    def test_isfinite_infinite_case_2(self) -> None:
        """Should test if an infinite DFA is finite (case #2)"""
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        dfa1 = DFA(
            states={"q0", "q1", "q2", "q3", "q4", "q5", "q6"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q2", "1": "q2"},
                "q2": {"0": "q3", "1": "q3"},
                "q3": {"0": "q4", "1": "q4"},
                "q4": {"0": "q5", "1": "q5"},
                "q5": {"0": "q6", "1": "q6"},
                "q6": {"0": "q6", "1": "q6"},
            },
            initial_state="q0",
            final_states={"q0", "q1", "q2", "q3", "q4", "q5", "q6"},
        )
        self.assertFalse(dfa1.isfinite())

    def test_isfinite_finite(self) -> None:
        """Should test if a finite DFA is finite"""
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        dfa = DFA.of_length({"0", "1"}, min_length=0, max_length=5)
        self.assertTrue(dfa.isfinite())

    def test_isfinite_empty(self) -> None:
        """Should test if an empty DFA is finite"""
        # This DFA has no reachable final states and
        # therefore is finite.
        dfa = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q0", "1": "q1"},
                "q3": {"0": "q2", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        self.assertTrue(dfa.isfinite())

    def test_isfinite_universe(self) -> None:
        # This DFA accepts all binary strings and
        # therefore is infinite.
        dfa = DFA.universal_language({"0", "1"})
        self.assertFalse(dfa.isfinite())

    def test_set_laws(self) -> None:
        """Tests many set laws that are true for all sets"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        input_symbols = {"0", "1"}
        contains_1111 = DFA.from_substring(input_symbols, "1111")
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        avoids_11 = DFA.from_substring(input_symbols, "11").complement(minify=False)
        # This DFA accepts all binary strings
        universal = DFA.universal_language(input_symbols)
        # This DFA represents the empty language
        empty = DFA.empty_language(input_symbols)
        # De Morgan's laws
        self.assertEqual(~(contains_1111 | avoids_11), ~contains_1111 & ~avoids_11)
        self.assertEqual(~(contains_1111 & avoids_11), ~contains_1111 | ~avoids_11)
        # Complement laws
        self.assertEqual(contains_1111 | ~contains_1111, universal)
        self.assertEqual(contains_1111 & ~contains_1111, empty)
        self.assertEqual(~universal, empty)
        self.assertEqual(~empty, universal)
        # Involution
        self.assertEqual(contains_1111, ~(~contains_1111))
        # Relationships between relative and absolute complements
        self.assertEqual(contains_1111 - avoids_11, contains_1111 & ~avoids_11)
        self.assertEqual(~(contains_1111 - avoids_11), ~contains_1111 | avoids_11)
        self.assertEqual(
            ~(contains_1111 - avoids_11), ~contains_1111 | (avoids_11 & contains_1111)
        )
        # Relationship with set difference
        self.assertEqual(~contains_1111 - ~avoids_11, avoids_11 - contains_1111)
        # Symmetric difference
        self.assertEqual(
            contains_1111 ^ avoids_11,
            (contains_1111 - avoids_11) | (avoids_11 - contains_1111),
        )
        self.assertEqual(
            contains_1111 ^ avoids_11,
            (contains_1111 | avoids_11) - (contains_1111 & avoids_11),
        )
        # Commutativity
        self.assertEqual(contains_1111 | avoids_11, avoids_11 | contains_1111)
        self.assertEqual(contains_1111 & avoids_11, avoids_11 & contains_1111)
        self.assertEqual(contains_1111 ^ avoids_11, avoids_11 ^ contains_1111)

    def test_minify_dfa(self) -> None:
        """Should minify a given DFA."""
        # This DFA accepts all words which are at least two characters long.
        # The states q1/q2 and q3/q4/q5/q6 are redundant.
        # The state q7 is not reachable.
        dfa = DFA(
            states={"q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q2"},
                "q1": {"0": "q3", "1": "q4"},
                "q2": {"0": "q5", "1": "q6"},
                "q3": {"0": "q3", "1": "q3"},
                "q4": {"0": "q4", "1": "q4"},
                "q5": {"0": "q5", "1": "q5"},
                "q6": {"0": "q6", "1": "q6"},
                "q7": {"0": "q7", "1": "q7"},
            },
            initial_state="q0",
            final_states={"q3", "q4", "q5", "q6"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(
            minimal_dfa.states,
            {
                frozenset(("q0",)),
                frozenset(("q1", "q2")),
                frozenset(("q3", "q4", "q5", "q6")),
            },
        )
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0",)): {
                    "0": frozenset(("q1", "q2")),
                    "1": frozenset(("q1", "q2")),
                },
                frozenset(("q1", "q2")): {
                    "0": frozenset(("q3", "q4", "q5", "q6")),
                    "1": frozenset(("q3", "q4", "q5", "q6")),
                },
                frozenset(("q3", "q4", "q5", "q6")): {
                    "0": frozenset(("q3", "q4", "q5", "q6")),
                    "1": frozenset(("q3", "q4", "q5", "q6")),
                },
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(
            minimal_dfa.final_states, {frozenset(("q3", "q4", "q5", "q6"))}
        )

    def test_minify_dfa_complex(self):
        """Should minify a given large DFA."""
        dfa = DFA(
            states={
                "13",
                "56",
                "18",
                "10",
                "15",
                "26",
                "24",
                "54",
                "32",
                "27",
                "5",
                "43",
                "8",
                "3",
                "17",
                "45",
                "57",
                "46",
                "35",
                "9",
                "0",
                "21",
                "39",
                "51",
                "6",
                "55",
                "47",
                "11",
                "20",
                "12",
                "59",
                "38",
                "44",
                "52",
                "16",
                "41",
                "1",
                "4",
                "28",
                "58",
                "48",
                "23",
                "22",
                "2",
                "31",
                "36",
                "34",
                "49",
                "40",
                "7",
                "25",
                "30",
                "53",
                "42",
                "33",
                "19",
                "50",
                "37",
                "14",
                "29",
            },
            input_symbols={"L", "U", "R", "D"},
            transitions={
                "55": {"L": "20", "U": "49", "R": "20", "D": "49"},
                "57": {"L": "5", "U": "6", "R": "1", "D": "46"},
                "35": {"L": "44", "U": "32", "R": "36", "D": "33"},
                "13": {"L": "45", "U": "23", "R": "45", "D": "23"},
                "43": {"L": "44", "U": "32", "R": "44", "D": "33"},
                "9": {"L": "5", "U": "6", "R": "1", "D": "6"},
                "53": {"L": "20", "U": "33", "R": "20", "D": "32"},
                "12": {"L": "40", "U": "23", "R": "25", "D": "11"},
                "42": {"L": "1", "U": "49", "R": "5", "D": "49"},
                "24": {"L": "40", "U": "48", "R": "25", "D": "23"},
                "27": {"L": "5", "U": "46", "R": "1", "D": "6"},
                "22": {"L": "40", "U": "48", "R": "25", "D": "11"},
                "19": {"L": "36", "U": "32", "R": "44", "D": "33"},
                "59": {"L": "40", "U": "48", "R": "45", "D": "11"},
                "39": {"L": "45", "U": "48", "R": "25", "D": "11"},
                "51": {"L": "20", "U": "18", "R": "20", "D": "18"},
                "34": {"L": "5", "U": "4", "R": "1", "D": "31"},
                "33": {"L": "44", "U": "0", "R": "36", "D": "28"},
                "23": {"L": "45", "U": "8", "R": "45", "D": "8"},
                "46": {"L": "44", "U": "0", "R": "44", "D": "28"},
                "58": {"L": "5", "U": "4", "R": "1", "D": "4"},
                "50": {"L": "20", "U": "28", "R": "20", "D": "0"},
                "54": {"L": "40", "U": "8", "R": "25", "D": "41"},
                "49": {"L": "1", "U": "18", "R": "5", "D": "18"},
                "21": {"L": "40", "U": "26", "R": "25", "D": "8"},
                "16": {"L": "5", "U": "31", "R": "1", "D": "4"},
                "6": {"L": "40", "U": "26", "R": "25", "D": "41"},
                "32": {"L": "36", "U": "0", "R": "44", "D": "28"},
                "48": {"L": "40", "U": "26", "R": "45", "D": "41"},
                "11": {"L": "45", "U": "26", "R": "25", "D": "41"},
                "15": {"L": "14", "U": "49", "R": "14", "D": "49"},
                "1": {"L": "56", "U": "6", "R": "37", "D": "46"},
                "3": {"L": "4", "U": "32", "R": "17", "D": "33"},
                "45": {"L": "8", "U": "23", "R": "8", "D": "23"},
                "52": {"L": "4", "U": "32", "R": "4", "D": "33"},
                "36": {"L": "56", "U": "6", "R": "37", "D": "6"},
                "20": {"L": "14", "U": "33", "R": "14", "D": "32"},
                "25": {"L": "47", "U": "23", "R": "10", "D": "11"},
                "29": {"L": "37", "U": "49", "R": "56", "D": "49"},
                "40": {"L": "47", "U": "48", "R": "10", "D": "23"},
                "5": {"L": "56", "U": "46", "R": "37", "D": "6"},
                "44": {"L": "47", "U": "48", "R": "10", "D": "11"},
                "38": {"L": "17", "U": "32", "R": "4", "D": "33"},
                "2": {"L": "47", "U": "48", "R": "8", "D": "11"},
                "30": {"L": "8", "U": "48", "R": "10", "D": "11"},
                "7": {"L": "14", "U": "18", "R": "14", "D": "18"},
                "37": {"L": "56", "U": "4", "R": "37", "D": "31"},
                "28": {"L": "4", "U": "0", "R": "17", "D": "28"},
                "8": {"L": "8", "U": "8", "R": "8", "D": "8"},
                "31": {"L": "4", "U": "0", "R": "4", "D": "28"},
                "17": {"L": "56", "U": "4", "R": "37", "D": "4"},
                "14": {"L": "14", "U": "28", "R": "14", "D": "0"},
                "10": {"L": "47", "U": "8", "R": "10", "D": "41"},
                "18": {"L": "37", "U": "18", "R": "56", "D": "18"},
                "47": {"L": "47", "U": "26", "R": "10", "D": "8"},
                "56": {"L": "56", "U": "31", "R": "37", "D": "4"},
                "4": {"L": "47", "U": "26", "R": "10", "D": "41"},
                "0": {"L": "17", "U": "0", "R": "4", "D": "28"},
                "26": {"L": "47", "U": "26", "R": "8", "D": "41"},
                "41": {"L": "8", "U": "26", "R": "10", "D": "41"},
            },
            initial_state="55",
            final_states={
                "15",
                "24",
                "54",
                "32",
                "27",
                "5",
                "43",
                "57",
                "3",
                "46",
                "35",
                "9",
                "21",
                "39",
                "51",
                "6",
                "55",
                "11",
                "20",
                "12",
                "59",
                "38",
                "44",
                "52",
                "16",
                "1",
                "58",
                "48",
                "22",
                "2",
                "36",
                "34",
                "49",
                "40",
                "25",
                "30",
                "53",
                "42",
                "33",
                "19",
                "50",
                "29",
            },
        )
        large_tuple = (
            "0",
            "10",
            "14",
            "17",
            "18",
            "23",
            "26",
            "28",
            "31",
            "37",
            "4",
            "41",
            "45",
            "47",
            "56",
            "8",
        )
        check_dfa = DFA(
            states={
                frozenset(("5",)),
                frozenset(("36",)),
                frozenset(("1",)),
                frozenset(("49",)),
                frozenset(("40",)),
                frozenset(("25",)),
                frozenset(("46",)),
                frozenset(("6",)),
                frozenset(("55",)),
                frozenset(large_tuple),
                frozenset(("33",)),
                frozenset(("11",)),
                frozenset(("20",)),
                frozenset(("48",)),
                frozenset(("44",)),
                frozenset(("32",)),
            },
            input_symbols={"L", "U", "R", "D"},
            transitions={
                frozenset(("48",)): {
                    "L": frozenset(("40",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("44",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("48",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("11",)),
                },
                frozenset(("40",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("48",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("33",)): {
                    "L": frozenset(("44",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("36",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("55",)): {
                    "L": frozenset(("20",)),
                    "U": frozenset(("49",)),
                    "R": frozenset(("20",)),
                    "D": frozenset(("49",)),
                },
                frozenset(("32",)): {
                    "L": frozenset(("36",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("44",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("46",)): {
                    "L": frozenset(("44",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("44",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("25",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("11",)),
                },
                frozenset(("6",)): {
                    "L": frozenset(("40",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("25",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("11",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("25",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("5",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("46",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("6",)),
                },
                frozenset(("49",)): {
                    "L": frozenset(("1",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("5",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(large_tuple): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("20",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("33",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("32",)),
                },
                frozenset(("36",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("6",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("6",)),
                },
                frozenset(("1",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("6",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("46",)),
                },
            },
            initial_state=frozenset(("55",)),
            final_states={
                frozenset(("5",)),
                frozenset(("1",)),
                frozenset(("36",)),
                frozenset(("49",)),
                frozenset(("40",)),
                frozenset(("25",)),
                frozenset(("46",)),
                frozenset(("6",)),
                frozenset(("55",)),
                frozenset(("33",)),
                frozenset(("11",)),
                frozenset(("20",)),
                frozenset(("48",)),
                frozenset(("44",)),
                frozenset(("32",)),
            },
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, check_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, check_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, check_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, check_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, check_dfa.final_states)

    def test_minify_minimal_dfa(self) -> None:
        """Should minify an already minimal DFA."""
        # This DFA just accepts words ending in 1.
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q1"}, "q1": {"0": "q0", "1": "q1"}},
            initial_state="q0",
            final_states={"q1"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        other_minimal_dfa = DFA(
            states={frozenset(("q0",)), frozenset(("q1",))},
            input_symbols={"0", "1"},
            transitions={
                frozenset(("q0",)): {"0": frozenset(("q0",)), "1": frozenset(("q1",))},
                frozenset(("q1",)): {"0": frozenset(("q0",)), "1": frozenset(("q1",))},
            },
            initial_state=frozenset(("q0",)),
            final_states={frozenset(("q1",))},
        )

        self.assertEqual(minimal_dfa.states, other_minimal_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, other_minimal_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, other_minimal_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, other_minimal_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, other_minimal_dfa.final_states)

    def test_minify_dfa_initial_state(self) -> None:
        """Should minify a DFA where the initial state is being changed."""
        # This DFA accepts all words with ones and zeroes.
        # The two states can be merged into one.
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q0", "1": "q0"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(("q0", "q1"))})
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q0", "q1")),
                }
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0", "q1")))
        self.assertEqual(minimal_dfa.final_states, {frozenset(("q0", "q1"))})

    def test_minify_dfa_no_final_states(self) -> None:
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q0", "1": "q0"},
            },
            initial_state="q0",
            final_states=set(),
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(("q0", "q1"))})
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q0", "q1")),
                },
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0", "q1")))
        self.assertEqual(minimal_dfa.final_states, set())

    def test_init_nfa_simple(self) -> None:
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": {"q0", "q1"}}, "q1": {"1": {"q2"}}, "q2": {}},
            initial_state="q0",
            final_states={"q2"},
        )
        dfa = DFA.from_nfa(nfa, retain_names=True, minify=False)
        self.assertEqual(
            dfa.states,
            {
                frozenset(),
                frozenset(("q0",)),
                frozenset(("q0", "q1")),
                frozenset(("q2",)),
            },
        )
        self.assertEqual(dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(): {"0": frozenset(), "1": frozenset()},
                frozenset(("q0",)): {"0": frozenset(("q0", "q1")), "1": frozenset()},
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q2",)),
                },
                frozenset(("q2",)): {"0": frozenset(), "1": frozenset()},
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(dfa.final_states, {frozenset(("q2",))})

    def test_init_nfa_more_complex(self) -> None:
        """Should convert to a DFA a more complex NFA."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": {"q0", "q1"}, "1": {"q0"}},
                "q1": {"0": {"q1"}, "1": {"q2"}},
                "q2": {"0": {"q2"}, "1": {"q1"}},
            },
            initial_state="q0",
            final_states={"q2"},
        )
        dfa = DFA.from_nfa(nfa, retain_names=True, minify=False)
        self.assertEqual(
            dfa.states,
            {
                frozenset(("q0",)),
                frozenset(("q0", "q1")),
                frozenset(("q0", "q2")),
                frozenset(("q0", "q1", "q2")),
            },
        )
        self.assertEqual(dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(("q0",)): {
                    "1": frozenset(("q0",)),
                    "0": frozenset(("q0", "q1")),
                },
                frozenset(("q0", "q1")): {
                    "1": frozenset(("q0", "q2")),
                    "0": frozenset(("q0", "q1")),
                },
                frozenset(("q0", "q2")): {
                    "1": frozenset(("q0", "q1")),
                    "0": frozenset(("q0", "q1", "q2")),
                },
                frozenset(("q0", "q1", "q2")): {
                    "1": frozenset(("q0", "q1", "q2")),
                    "0": frozenset(("q0", "q1", "q2")),
                },
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(
            dfa.final_states, {frozenset(("q0", "q1", "q2")), frozenset(("q0", "q2"))}
        )

    def test_init_nfa_lambda_transition(self) -> None:
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA.from_nfa(self.nfa, retain_names=True, minify=False)
        self.assertEqual(
            dfa.states, {frozenset(), frozenset(("q0",)), frozenset(("q1", "q2"))}
        )
        self.assertEqual(dfa.input_symbols, {"a", "b"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(): {"a": frozenset(), "b": frozenset()},
                frozenset(("q0",)): {"a": frozenset(("q1", "q2")), "b": frozenset()},
                frozenset(("q1", "q2")): {
                    "a": frozenset(("q1", "q2")),
                    "b": frozenset(("q0",)),
                },
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(dfa.final_states, {frozenset(("q1", "q2"))})

    def test_nfa_to_dfa_with_lambda_transitions(self) -> None:
        """Test NFA->DFA when initial state has lambda transitions"""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={"q0": {"": {"q2"}}, "q1": {"a": {"q1"}}, "q2": {"a": {"q1"}}},
            initial_state="q0",
            final_states={"q1"},
        )
        dfa = DFA.from_nfa(
            nfa, retain_names=True, minify=False
        )  # returns an equivalent DFA
        self.assertEqual(dfa.read_input("a"), frozenset(("q1",)))

    def test_partial_dfa(self) -> None:
        """Should allow for partial DFA when flag is set"""
        dfa = DFA(
            states={"", "a", "b", "aa", "bb", "ab", "ba"},
            input_symbols={"a", "b"},
            transitions={
                "": {"a": "a", "b": "b"},
                "a": {"b": "ab", "a": "aa"},
                "b": {"b": "bb"},
                "aa": {"a": "aa", "b": "ab"},
                "bb": {"a": "ba"},
                "ab": {"b": "bb"},
                "ba": {"a": "aa"},
            },
            initial_state="",
            final_states={"aa"},
            allow_partial=True,
        )
        self.assertEqual(dfa.read_input("aa"), "aa")

    def test_show_diagram_initial_final_different(self) -> None:
        """
        Should construct the diagram for a DFA whose initial state
        is not a final state.
        """
        graph = self.dfa.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.dfa.states).issubset(node_names))
        self.assertEqual(len(self.dfa.states) + 1, len(node_names))

        for state in self.dfa.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.dfa.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", "0", "q0"),
            ("q0", "1", "q1"),
            ("q1", "0", "q0"),
            ("q1", "1", "q2"),
            ("q2", "0", "q2"),
            ("q2", "1", "q1"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, self.dfa.initial_state)
        self.assertTrue(source not in self.dfa.states)

    def test_show_diagram_read_input(self) -> None:
        """
        Should construct the diagram for a DFA reading input.
        """
        input_strings = ["0111", "001", "01110011", "001011001", "1100", ""]

        for input_string in input_strings:
            graph = self.dfa.show_diagram(input_str=input_string)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            colored_edges.sort(key=lambda edge: edge.attr["label"][2:])

            edge_pairs = [
                edge[0:2] for edge in self.dfa._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_initial_final_same(self) -> None:
        """
        Should construct the diagram for a DFA whose initial state
        is also a final state.
        """
        # This DFA accepts all words which do not contain two consecutive
        # occurrences of 1
        dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )

        graph = dfa.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(dfa.states).issubset(node_names))
        self.assertEqual(len(dfa.states) + 1, len(node_names))

        for state in self.dfa.states:
            node = graph.get_node(state)
            expected_shape = "doublecircle" if state in dfa.final_states else "circle"
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", "0", "q0"),
            ("q0", "1", "q1"),
            ("q1", "0", "q0"),
            ("q1", "1", "q2"),
            ("q2", "0,1", "q2"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, dfa.initial_state)
        self.assertTrue(source not in dfa.states)

    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a DFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, "test_dfa.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.dfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_repr_mimebundle_same(self) -> None:
        """
        Check that the mimebundle is the same.
        """

        random.seed(42)
        first_repr = self.dfa._repr_mimebundle_()
        random.seed(42)
        second_repr = self.dfa.show_diagram()._repr_mimebundle_()
        self.assertEqual(first_repr, second_repr)

    def test_show_diagram_orientations(self) -> None:
        graph = self.dfa.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")
        graph = self.dfa.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")
        graph = self.dfa.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")
        graph = self.dfa.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_fig_size(self) -> None:
        """
        Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering).
        """
        graph = self.dfa.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.dfa.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")

    def test_minimal_finite_language(self):
        """Should compute the minimal DFA accepting the given finite language"""

        # Same language described in the book this algorithm comes from
        language = {
            "aa",
            "aaa",
            "aaba",
            "aabbb",
            "abaa",
            "ababb",
            "abbab",
            "baa",
            "babb",
            "bbaa",
            "bbabb",
            "bbbab",
        }

        equiv_dfa = DFA(
            states=set(range(10)),
            input_symbols={"a", "b"},
            transitions={
                0: {"a": 0, "b": 0},
                1: {"a": 2, "b": 3},
                2: {"a": 4, "b": 5},
                3: {"a": 7, "b": 5},
                4: {"a": 9, "b": 7},
                5: {"a": 7, "b": 6},
                6: {"a": 8, "b": 0},
                7: {"a": 9, "b": 8},
                8: {"a": 0, "b": 9},
                9: {"a": 0, "b": 0},
            },
            initial_state=1,
            final_states={4, 9},
        )

        minimal_dfa = DFA.from_finite_language({"a", "b"}, language)

        self.assertEqual(len(minimal_dfa.states), len(equiv_dfa.states))
        self.assertEqual(minimal_dfa, equiv_dfa)

    def test_minimal_finite_language_large(self) -> None:
        """Should compute the minimal DFA accepting the given finite language on
        large test case"""
        m = 50
        n = 50
        language = {("a" * i + "b" * j) for i, j in product(range(n), range(m))}

        equiv_dfa = DFA.from_finite_language({"a", "b"}, language)
        minimal_dfa = equiv_dfa.minify()

        self.assertEqual(equiv_dfa, minimal_dfa)
        self.assertEqual(len(equiv_dfa.states), len(minimal_dfa.states))

        dfa_language = {word for word in equiv_dfa}
        self.assertEqual(dfa_language, language)

    def test_dfa_repr(self) -> None:
        """Should display proper string representation of DFA"""
        dfa = DFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
            allow_partial=False,
        )
        self.assertEqual(
            repr(dfa),
            "DFA(states={'q0'}, input_symbols={'a'}, transitions={'q0': {'a': 'q0'}}, "
            "initial_state='q0', final_states={'q0'}, allow_partial=False)",
        )

    def test_iter_finite(self) -> None:
        """
        Test that DFA for finite language generates all words
        """
        language = {
            "aa",
            "aaa",
            "aaba",
            "aabbb",
            "abaa",
            "ababb",
            "abbab",
            "baa",
            "babb",
            "bbaa",
            "bbabb",
            "bbbab",
        }
        dfa = DFA.from_finite_language({"a", "b"}, language)
        generated_set = {word for word in dfa}
        self.assertEqual(generated_set, language)

    def test_iter_infinite(self) -> None:
        """
        Test that language that avoids the pattern '11' generates the correct
        values in correct order
        """
        dfa = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )

        generator = iter(dfa)
        expected = [
            "",
            "0",
            "1",
            "00",
            "01",
            "10",
            "000",
            "001",
            "010",
            "100",
            "101",
            "0000",
            "0001",
            "0010",
            "0100",
            "0101",
            "1000",
            "1001",
            "1010",
        ]
        generated_list = [next(generator) for _ in expected]
        self.assertEqual(generated_list, expected)

    def test_len_finite(self) -> None:
        input_symbols = {"a", "b"}
        dfa = DFA.from_finite_language(input_symbols, set())
        self.assertEqual(len(dfa), 0)
        dfa = DFA.from_finite_language(input_symbols, {""})
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(input_symbols, {"a"})
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(input_symbols, {"ababababab"})
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(input_symbols, {"a" * i for i in range(5)})
        self.assertEqual(len(dfa), 5)
        dfa = DFA.from_finite_language(
            input_symbols, {"a" * i + "b" * j for i in range(5) for j in range(5)}
        )
        self.assertEqual(len(dfa), 25)

    def test_len_infinite(self) -> None:
        dfa = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        with self.assertRaises(exceptions.InfiniteLanguageException):
            len(dfa)
        with self.assertRaises(exceptions.InfiniteLanguageException):
            len(~dfa)

    def test_random_word(self) -> None:
        """
        Test random generation of words, the generation should be uniformly random
        """
        binary = {"0", "1"}
        dfa = DFA.from_prefix(binary, "00")
        with self.assertRaises(ValueError):
            dfa.random_word(1)

        for i in range(10):
            self.assertEqual(dfa.random_word(2), "00")

        for i in range(10):
            self.assertIn(dfa.random_word(10), dfa)

        for i in range(10):
            self.assertIn(dfa.random_word(100), dfa)

    def test_predecessor(self) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language)
        expected = sorted(language, reverse=True)
        actual = list(dfa.predecessors("11111111111111111111111111111111"))
        self.assertListEqual(actual, expected)
        expected = sorted({"", "0", "00", "000", "010"}, reverse=True)
        actual = list(dfa.predecessors("010", strict=False))

        self.assertEqual(dfa.predecessor("000"), "00")
        self.assertEqual(dfa.predecessor("0100"), "010")
        self.assertEqual(dfa.predecessor("1"), "010101111111101011010100")
        self.assertEqual(
            dfa.predecessor("0111111110101011"), "010101111111101011010100"
        )
        self.assertIsNone(dfa.predecessor(""))

        infinite_dfa = DFA.from_nfa(NFA.from_regex("0*1*"))
        with self.assertRaises(exceptions.InfiniteLanguageException):
            infinite_dfa.predecessor("000")
        with self.assertRaises(exceptions.InfiniteLanguageException):
            [_ for _ in infinite_dfa.predecessors("000")]

    def test_successor(self) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language)
        expected = sorted(language)
        actual = list(dfa.successors("", strict=False))
        self.assertListEqual(actual, expected)

        self.assertEqual(dfa.successor("000"), "010")
        self.assertEqual(dfa.successor("0100"), "010101111111101011010100")
        self.assertIsNone(dfa.successor("110"))
        self.assertIsNone(dfa.successor("111111110101011"))

        infinite_dfa = DFA.from_nfa(NFA.from_regex("0*1*"))
        self.assertEqual(infinite_dfa.successor(""), "0")
        self.assertEqual(infinite_dfa.successor("0"), "00")
        self.assertEqual(infinite_dfa.successor("00"), "000")
        self.assertEqual(infinite_dfa.successor("0001"), "00011")
        self.assertEqual(infinite_dfa.successor("00011"), "000111")
        self.assertEqual(infinite_dfa.successor("0000000011111"), "00000000111111")
        self.assertEqual(infinite_dfa.successor("1"), "11")
        self.assertEqual(infinite_dfa.successor(100 * "0"), 101 * "0")
        self.assertEqual(infinite_dfa.successor(100 * "1"), 101 * "1")

    def test_successor_and_predecessor(self) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language)
        for word in language:
            self.assertEqual(dfa.successor(dfa.predecessor(word)), word)  # type: ignore
            self.assertEqual(dfa.predecessor(dfa.successor(word)), word)  # type: ignore

    def test_successor_custom_key(self) -> None:
        input_symbols = {"a", "b", "c", "d"}
        order = {"b": 0, "c": 1, "a": 2, "d": 3}
        expected = [
            "",
            "b",
            "ba",
            "bab",
            "bad",
            "c",
            "cd",
            "cda",
            "a",
            "ab",
            "ac",
            "aa",
            "ad",
            "dddddddddddddddddb",
            "dddddddddddddddddd",
        ]
        language = set(expected)
        dfa = DFA.from_finite_language(input_symbols, language)
        actual = list(dfa.successors(None, key=order.get))
        self.assertListEqual(actual, expected)

    def test_successor_partial(self) -> None:
        binary = {"0", "1"}
        dfa = DFA(
            states={0, 1},
            input_symbols=binary,
            transitions={0: {"0": 1}, 1: {"1": 1}},
            initial_state=0,
            final_states={1},
            allow_partial=True,
        )
        self.assertEqual(dfa.successor(None), "0")
        self.assertEqual(dfa.successor(""), "0")
        self.assertEqual(dfa.successor("0"), "01")
        self.assertEqual(dfa.successor("00"), "01")
        self.assertEqual(dfa.successor("0000101010111"), "01")
        self.assertEqual(dfa.successor("01"), "011")
        self.assertEqual(dfa.successor("01000"), "011")
        self.assertEqual(dfa.successor("1"), None)

    def test_count_words_of_length(self) -> None:
        """
        Test that language that avoids the pattern '11' is counted by fibonacci numbers
        """
        dfa = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )

        fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i, fib in enumerate(fibonacci):
            self.assertEqual(dfa.count_words_of_length(i), fib)

    def test_words_of_length(self) -> None:
        """
        Test that all words generated are accepted and that count matches
        """
        dfa = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )

        fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i, fib in enumerate(fibonacci):
            count = 0
            for word in dfa.words_of_length(i):
                count += 1
                self.assertIn(word, dfa)
            self.assertEqual(count, fib)

    def test_minimum_word_length(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        at_least_four_ones = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_11_occurrence = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        # This DFA accepts all binary strings except the empty string
        at_least_one_symbol = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q1", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        # This DFA represents the empty language
        empty = DFA(
            states={"q0"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q0"}},
            initial_state="q0",
            final_states=set(),
        )

        self.assertEqual(at_least_four_ones.minimum_word_length(), 4)
        self.assertEqual(no_11_occurrence.minimum_word_length(), 0)
        self.assertEqual(at_least_one_symbol.minimum_word_length(), 1)
        with self.assertRaises(exceptions.EmptyLanguageException):
            empty.minimum_word_length()

    def test_maximum_word_length(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        at_least_four_ones = DFA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q3"},
                "q3": {"0": "q3", "1": "q4"},
                "q4": {"0": "q4", "1": "q4"},
            },
            initial_state="q0",
            final_states={"q4"},
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_11_occurrence = DFA(
            states={"p0", "p1", "p2"},
            input_symbols={"0", "1"},
            transitions={
                "p0": {"0": "p0", "1": "p1"},
                "p1": {"0": "p0", "1": "p2"},
                "p2": {"0": "p2", "1": "p2"},
            },
            initial_state="p0",
            final_states={"p0", "p1"},
        )
        # This DFA accepts all binary strings except the empty string
        at_most_one_symbol = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q2", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        # This DFA represents the empty language
        empty = DFA(
            states={"q0"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q0"}},
            initial_state="q0",
            final_states=set(),
        )

        self.assertEqual(at_least_four_ones.maximum_word_length(), None)
        self.assertEqual(no_11_occurrence.maximum_word_length(), None)
        self.assertEqual(at_most_one_symbol.maximum_word_length(), 1)
        with self.assertRaises(exceptions.EmptyLanguageException):
            empty.maximum_word_length()

    def test_contains_prefix(self) -> None:
        input_symbols = {"a", "n", "o", "b"}

        prefix_dfa = DFA.from_prefix(input_symbols, "nano")
        self.assertEqual(len(prefix_dfa.states), len(prefix_dfa.minify().states))

        subset_dfa = DFA.from_finite_language(
            input_symbols, {"nano", "nanobao", "nanonana", "nanonano", "nanoo"}
        )
        self.assertTrue(subset_dfa < prefix_dfa)

        self.assertEqual(
            ~prefix_dfa, DFA.from_prefix(input_symbols, "nano", contains=False)
        )

        for word in prefix_dfa:
            if len(word) > 8:
                break
            self.assertTrue(word.startswith("nano"))

    def test_contains_suffix(self) -> None:
        input_symbols = {"a", "n", "o", "b"}

        suffix_dfa = DFA.from_suffix(input_symbols, "nano")
        self.assertEqual(len(suffix_dfa.states), len(suffix_dfa.minify().states))

        subset_dfa = DFA.from_finite_language(
            input_symbols,
            {"nano", "annnano", "bnano", "anbonano", "nananananananananano"},
        )
        self.assertTrue(subset_dfa < suffix_dfa)

        self.assertEqual(
            ~suffix_dfa, DFA.from_suffix(input_symbols, "nano", contains=False)
        )

        for word in suffix_dfa:
            if len(word) > 8:
                break
            self.assertTrue(word.endswith("nano"))

    def test_contains_substring(self) -> None:
        """Should compute the minimal DFA accepting strings with the given substring"""

        input_symbols = {"a", "n", "o", "b"}

        equiv_dfa = DFA(
            states={"", "n", "na", "nan", "nano"},
            input_symbols=input_symbols,
            transitions={
                "": {"a": "", "n": "n", "o": "", "b": ""},
                "n": {"a": "na", "n": "n", "o": "", "b": ""},
                "na": {"a": "", "n": "nan", "o": "", "b": ""},
                "nan": {"a": "na", "n": "n", "o": "nano", "b": ""},
                "nano": {"a": "nano", "n": "nano", "o": "nano", "b": "nano"},
            },
            initial_state="",
            final_states={"nano"},
        )

        substring_dfa = DFA.from_substring(input_symbols, "nano")
        self.assertEqual(len(substring_dfa.states), len(substring_dfa.minify().states))

        self.assertEqual(len(substring_dfa.states), len(equiv_dfa.states))
        self.assertEqual(substring_dfa, equiv_dfa)

        subset_dfa = DFA.from_finite_language(
            input_symbols, {"nano", "bananano", "nananano", "naonano"}
        )
        self.assertTrue(subset_dfa < substring_dfa)

        self.assertEqual(
            ~substring_dfa, DFA.from_substring(input_symbols, "nano", contains=False)
        )

        for word in substring_dfa:
            if len(word) > 8:
                break
            self.assertIn("nano", word)

    def test_contains_subsequence(self) -> None:
        """Should compute the minimal DFA accepting strings with the given
        subsequence"""

        input_symbols = {"a", "n", "o", "b"}

        equiv_dfa = DFA(
            states={"", "n", "na", "nan", "nano"},
            input_symbols=input_symbols,
            transitions={
                "": {"a": "", "n": "n", "o": "", "b": ""},
                "n": {"a": "na", "n": "n", "o": "n", "b": "n"},
                "na": {"a": "na", "n": "nan", "o": "na", "b": "na"},
                "nan": {"a": "nan", "n": "nan", "o": "nano", "b": "nan"},
                "nano": {"a": "nano", "n": "nano", "o": "nano", "b": "nano"},
            },
            initial_state="",
            final_states={"nano"},
        )

        subsequence_dfa = DFA.from_subsequence(input_symbols, "nano")
        self.assertEqual(
            len(subsequence_dfa.states), len(subsequence_dfa.minify().states)
        )

        self.assertEqual(len(subsequence_dfa.states), len(equiv_dfa.states))
        self.assertEqual(subsequence_dfa, equiv_dfa)

        subset_dfa = DFA.from_finite_language(
            input_symbols, {"naooono", "bananano", "onbaonbo", "ooonano"}
        )
        self.assertTrue(subset_dfa < subsequence_dfa)

        substring_dfa = DFA.from_substring(
            input_symbols,
            "nano",
        )
        self.assertTrue(substring_dfa < subsequence_dfa)

        self.assertEqual(
            ~subsequence_dfa,
            DFA.from_subsequence(input_symbols, "nano", contains=False),
        )

    def test_of_length(self) -> None:
        binary = {"0", "1"}
        dfa1 = DFA.of_length(binary)
        self.assertFalse(dfa1.isfinite())
        self.assertEqual(len(dfa1.states), len(dfa1.minify().states))
        self.assertEqual(dfa1, DFA.universal_language(binary))
        self.assertEqual(dfa1.minimum_word_length(), 0)
        self.assertEqual(dfa1.maximum_word_length(), None)

        dfa2 = DFA.of_length(binary, min_length=5)
        self.assertFalse(dfa2.isfinite())
        self.assertEqual(len(dfa2.states), len(dfa2.minify().states))
        generator = iter(dfa2)
        for word in generator:
            if len(word) > 8:
                break
            self.assertTrue(len(word) >= 5)
        self.assertEqual(dfa2.minimum_word_length(), 5)
        self.assertEqual(dfa2.maximum_word_length(), None)

        dfa3 = DFA.of_length(binary, min_length=0, max_length=4)
        self.assertTrue(dfa3.isfinite())
        self.assertEqual(len(dfa3.states), len(dfa3.minify().states))
        expected = [
            "",
            "0",
            "1",
            "00",
            "01",
            "10",
            "11",
            "000",
            "001",
            "010",
            "011",
            "100",
            "101",
            "110",
            "111",
            "0000",
            "0001",
            "0010",
            "0011",
            "0100",
            "0101",
            "0110",
            "0111",
            "1000",
            "1001",
            "1010",
            "1011",
            "1100",
            "1101",
            "1110",
            "1111",
        ]
        self.assertListEqual(list(dfa3), expected)
        self.assertEqual(dfa3, DFA.from_finite_language(binary, set(expected)))
        self.assertEqual(dfa1, dfa2.union(dfa3))
        self.assertEqual(dfa3.minimum_word_length(), 0)
        self.assertEqual(dfa3.maximum_word_length(), 4)

        dfa4 = DFA.of_length(binary, min_length=4, max_length=8)
        self.assertTrue(dfa4.isfinite())
        self.assertEqual(len(dfa4.states), len(dfa4.minify().states))
        expected_counts = [
            0,
            0,
            0,
            0,
            2**4,
            2**5,
            2**6,
            2**7,
            2**8,
            0,
            0,
            0,
            0,
        ]
        actual_counts = [
            dfa4.count_words_of_length(i) for i, _ in enumerate(expected_counts)
        ]
        self.assertListEqual(actual_counts, expected_counts)
        self.assertEqual(dfa4.minimum_word_length(), 4)
        self.assertEqual(dfa4.maximum_word_length(), 8)

        dfa5 = DFA.of_length(binary, min_length=2, max_length=2, symbols_to_count={"1"})
        dfa6 = DFA(
            states={0, 1, 2, 3},
            input_symbols=binary,
            transitions={
                0: {"1": 1, "0": 0},
                1: {"1": 2, "0": 1},
                2: {"1": 3, "0": 2},
                3: {"1": 3, "0": 3},
            },
            initial_state=0,
            final_states={2},
        )
        self.assertEqual(dfa5, dfa6)

        dfa7 = DFA.of_length(binary, symbols_to_count={"1"})
        dfa8 = DFA.of_length(binary, symbols_to_count={"0"})

        self.assertEqual(dfa7.union(dfa8), DFA.universal_language(binary))

    def test_count_mod(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            _ = DFA.count_mod(binary, 0)

        no_symbols = DFA.count_mod(binary, 4, symbols_to_count=set())
        self.assertEqual(no_symbols, DFA.universal_language(binary))

        no_symbols_empty = DFA.count_mod(
            binary, 4, remainders={1, 2, 3}, symbols_to_count=set()
        )
        self.assertEqual(no_symbols_empty, DFA.empty_language(binary))

        even = DFA.count_mod(binary, 2)
        for word in even:
            if len(word) >= 8:
                break
            self.assertEqual(len(word) % 2, 0)

        odd = DFA.count_mod(binary, 2, remainders={1})
        for word in odd:
            if len(word) >= 8:
                break
            self.assertEqual(len(word) % 2, 1)

        even_1 = DFA.count_mod(binary, 2, symbols_to_count={"1"})
        for word in even_1:
            if len(word) >= 8:
                break
            self.assertEqual(word.count("1") % 2, 0)

        odd_0 = DFA.count_mod(binary, 2, remainders={1}, symbols_to_count={"0"})
        for word in odd_0:
            if len(word) >= 8:
                break
            self.assertEqual(word.count("0") % 2, 1)

        self.assertEqual(
            DFA.count_mod(binary, 4, remainders={0, 2}), DFA.count_mod(binary, 2)
        )

    def test_nth_from_start(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            dfa = DFA.nth_from_start(binary, "0", 0)

        with self.assertRaises(exceptions.InvalidSymbolError):
            dfa = DFA.nth_from_start(binary, "2", 1)

        dfa = DFA.nth_from_start({"0"}, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertListEqual(list(~dfa), [""])
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_start(binary, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertIn("00", dfa)
        self.assertIn("01", dfa)
        self.assertNotIn("10", dfa)
        self.assertNotIn("11", dfa)
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_start(binary, "0", 2)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertIn("00", dfa)
        self.assertNotIn("01", dfa)
        self.assertIn("10", dfa)
        self.assertNotIn("11", dfa)
        self.assertEqual(dfa.minimum_word_length(), 2)

        dfa = DFA.nth_from_start(binary, "0", 3)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 3)

        dfa = DFA.nth_from_start(binary, "1", 4)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 4)

    def test_nth_from_end(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            dfa = DFA.nth_from_end(binary, "0", 0)

        with self.assertRaises(exceptions.InvalidSymbolError):
            dfa = DFA.nth_from_end(binary, "2", 1)

        dfa = DFA.nth_from_end({"0"}, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_end(binary, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_end(binary, "0", 2)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 2)

        dfa = DFA.nth_from_end(binary, "0", 3)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 3)

        dfa = DFA.nth_from_end(binary, "1", 4)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 4)

    def test_empty_language(self) -> None:
        dfa = DFA.empty_language({"0"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"0", "1"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"a", "b"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"0", "1", "a", "b"})
        self.assertTrue(dfa.isempty())
