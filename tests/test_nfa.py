#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.fa.fa as fa
import tests.test_fa as test_fa
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = NFA(self.nfa)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_copy_nfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_dfa(self):
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA(self.dfa)
        nose.assert_equal(nfa.states, {'q0', 'q1', 'q2'})
        nose.assert_equal(nfa.input_symbols, {'0', '1'})
        nose.assert_equal(nfa.transitions, {
            'q0': {'0': {'q0'}, '1': {'q1'}},
            'q1': {'0': {'q0'}, '1': {'q2'}},
            'q2': {'0': {'q2'}, '1': {'q1'}}
        })
        nose.assert_equal(nfa.initial_state, 'q0')

    @patch('automata.fa.nfa.NFA.validate_self')
    def test_init_validation(self, validate_self):
        """Should validate NFA when initialized."""
        NFA(self.nfa)
        validate_self.assert_called_once_with()

    def test_nfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_nfa = self.nfa.copy()
        nose.assert_true(self.nfa == new_nfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_nfa = self.nfa.copy()
        new_nfa.final_states.add('q2')
        nose.assert_true(self.nfa != new_nfa, 'NFAs are equal')

    def test_validate_self_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(fa.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate_self()

    def test_validate_self_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(fa.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q3'}
            self.nfa.validate_self()

    def test_validate_self_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(fa.InvalidStateError):
            self.nfa.initial_state = 'q3'
            self.nfa.validate_self()

    def test_validate_self_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(fa.InvalidStateError):
            self.nfa.final_states = {'q3'}
            self.nfa.validate_self()

    def test_validate_input_valid(self):
        """Should return correct stop states if valid NFA input is given."""
        nose.assert_equal(self.nfa.validate_input('aba'), {'q1', 'q2'})

    def test_validate_self_missing_state(self):
        """Should silently ignore states without transitions defined."""
        self.nfa.states.add('q3')
        self.nfa.transitions['q0']['a'].add('q3')
        nose.assert_equal(self.nfa.validate_self(), True)

    def test_validate_input_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(fa.InvalidSymbolError):
            self.nfa.validate_input('abc')

    def test_validate_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(fa.RejectionError):
            self.nfa.validate_input('abba')

    def test_validate_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.validate_input('aba', step=True)
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        nose.assert_equal(list(validation_generator), [
            {'q0'}, {'q1', 'q2'}, {'q0'}, {'q1', 'q2'}
        ])

    def test_cyclic_lambda_transitions(self):
        """Should traverse NFA containing cyclic lambda transitions."""
        # NFA which matches zero or more occurrences of 'a'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a'},
            transitions={
                'q0': {'': {'q1', 'q3'}},
                'q1': {'a': {'q2'}},
                'q2': {'': {'q3'}},
                'q3': {'': {'q0'}}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_equal(nfa.validate_input(''), {'q0', 'q1', 'q3'})
        nose.assert_equal(nfa.validate_input('a'), {'q0', 'q1', 'q2', 'q3'})
