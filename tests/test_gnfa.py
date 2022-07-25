#!/usr/bin/env python3
"""Classes and functions for testing the behavior of GNFAs."""

import types
from unittest.mock import patch

import unittest

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA


class TestGNFA(test_fa.TestFA):
    """A test class for testing generalised nondeterministic finite automata."""

    def test_init_gnfa(self):
        """Should copy GNFA if passed into NFA constructor."""
        new_gnfa = GNFA.copy(self.gnfa)
        self.assert_is_copy_for_gnfa(new_gnfa, self.gnfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            GNFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_state='q1'
            )

    def test_copy_gnfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_gnfa = self.gnfa.copy()
        self.assert_is_copy_for_gnfa(new_gnfa, self.gnfa)

    def test_init_dfa(self):
        """Should convert DFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_dfa(self.dfa)
        self.assertEqual(gnfa.states, {0, 1, 'q2', 'q0', 'q1'})
        self.assertEqual(gnfa.input_symbols, {'0', '1'})
        self.assertEqual(gnfa.transitions, {
            'q0': {'q0': '0', 'q1': '1', 1: None, 'q2': None},
            'q1': {'q0': '0', 'q2': '1', 1: '', 'q1': None},
            'q2': {'q2': '0', 'q1': '1', 1: None, 'q0': None},
            0: {'q0': '', 1: None, 'q1': None, 'q2': None}
        })
        self.assertEqual(gnfa.initial_state, 0)

    def test_init_nfa(self):
        """Should convert NFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_nfa(self.nfa)
        self.assertEqual(gnfa.states, {0, 1, 'q0', 'q1'})
        self.assertEqual(gnfa.input_symbols, {'b', 'a'})
        self.assertEqual(gnfa.transitions, {
            'q0': {'q1': 'a', 1: None, 'q0': None},
            'q1': {'q1': 'a', 'q0': 'b', 1: ''},
            0: {'q0': '', 1: None, 'q1': None}
        })
        self.assertEqual(gnfa.initial_state, 0)

    @patch('automata.fa.gnfa.GNFA.validate')
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        GNFA.copy(self.gnfa)
        validate.assert_called_once_with()

    def test_gnfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_gnfa = self.gnfa.copy()
        self.assertTrue(self.gnfa == new_gnfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_gnfa = self.gnfa.copy()
        new_gnfa.states.add('q2')
        self.assertTrue(self.nfa != new_gnfa, 'NFAs are equal')

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidRegExError):
            self.gnfa.transitions['q1']['q2'] = {'c'}
            self.gnfa.validate()

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.nfa.transitions['q1']['q3'] = {'a'}
            self.nfa.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.gnfa.initial_state = 'q3'
            self.gnfa.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            del self.gnfa.transitions[self.gnfa.initial_state]
            self.gnfa.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.gnfa.final_state = 'q3'
            self.gnfa.validate()

    def test_validate_missing_state(self):
        """Should raise an error if some transitions are missing."""
        with self.assertRaises(exceptions.MissingStateError):
            self.gnfa.states.add('q3')
            self.gnfa.validate()

    def test_to_regex(self):
        """
        We generate GNFA from DFA then convert it to regex
        then generate NFA from regex (already tested method)
        and check for equivalence of NFA and previous DFA
        """

        gnfa = GNFA.from_dfa(self.dfa)
        regex = gnfa.to_regex()
        nfa = NFA.from_regex(regex)
        dfa2 = DFA.from_nfa(nfa)

        self.assertEqual(self.dfa, dfa2)
