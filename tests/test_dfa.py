#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.fa as FA
import tests.test_fa as test_fa
from automata.dfa import DFA
from automata.nfa import NFA


class TestDFA(test_fa.TestFA):
    """A test class for testing deterministic finite automata."""

    def test_init_dfa(self):
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = DFA(self.dfa)
        self.assert_is_copy(new_dfa, self.dfa)

    def test_copy_dfa(self):
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assert_is_copy(new_dfa, self.dfa)

    @patch('automata.dfa.DFA.validate_self')
    def test_init_validation(self, validate_self):
        """Should validate DFA when initialized."""
        DFA(self.dfa)
        validate_self.assert_called_once_with()

    def test_dfa_equal(self):
        """Should correctly determine if two DFAs are equal."""
        new_dfa = self.dfa.copy()
        nose.assert_true(self.dfa == new_dfa, 'DFAs are not equal')

    def test_dfa_not_equal(self):
        """Should correctly determine if two DFAs are not equal."""
        new_dfa = self.dfa.copy()
        new_dfa.final_states.add('q2')
        nose.assert_true(self.dfa != new_dfa, 'DFAs are not equal')

    def test_validate_self_missing_state(self):
        """Should raise error if a state has no transitions defined."""
        with nose.assert_raises(FA.MissingTransitionError):
            del self.dfa.transitions['q1']
            self.dfa.validate_self()

    def test_validate_self_missing_symbol(self):
        """Should raise error if a symbol transition is missing."""
        with nose.assert_raises(FA.MissingTransitionError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate_self()

    def test_validate_self_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(FA.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate_self()

    def test_validate_self_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(FA.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate_self()

    def test_validate_self_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(FA.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate_self()

    def test_validate_self_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(FA.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate_self()

    def test_validate_input_valid(self):
        """Should return correct stop state if valid DFA input is given."""
        nose.assert_equal(self.dfa.validate_input('0111'), 'q1')

    def test_validate_input_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(FA.InvalidSymbolError):
            self.dfa.validate_input('01112')

    def test_validate_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(FA.RejectionError):
            self.dfa.validate_input('011')

    def test_validate_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dfa.validate_input('0111', step=True)
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        nose.assert_equal(list(validation_generator), [
            'q0', 'q0', 'q1', 'q2', 'q1'
        ])

    def test_init_nfa_simple(self):
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}},
                'q1': {'1': {'q2'}},
                'q2': {}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA(nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q0,q1}', '{q2}'})
        nose.assert_equal(dfa.input_symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'0': '{}', '1': '{}'},
            '{q0}': {'0': '{q0,q1}', '1': '{}'},
            '{q0,q1}': {'0': '{q0,q1}', '1': '{q2}'},
            '{q2}': {'0': '{}', '1': '{}'}
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q2}'})

    def test_init_nfa_lambda_transition(self):
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA(self.nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q1,q2}'})
        nose.assert_equal(dfa.input_symbols, {'a', 'b'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'a': '{}', 'b': '{}'},
            '{q0}': {'a': '{q1,q2}', 'b': '{}'},
            '{q1,q2}': {'a': '{q1,q2}', 'b': '{q0}'},
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q1,q2}'})
