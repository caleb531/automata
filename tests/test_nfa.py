#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""

import types
from unittest.mock import patch

import unittest

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = NFA.copy(self.nfa)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            NFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_nfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_dfa(self):
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA.from_dfa(self.dfa)
        self.assertEqual(nfa.states, {'q0', 'q1', 'q2'})
        self.assertEqual(nfa.input_symbols, {'0', '1'})
        self.assertEqual(nfa.transitions, {
            'q0': {'0': {'q0'}, '1': {'q1'}},
            'q1': {'0': {'q0'}, '1': {'q2'}},
            'q2': {'0': {'q2'}, '1': {'q1'}}
        })
        self.assertEqual(nfa.initial_state, 'q0')

    @patch('automata.fa.nfa.NFA.validate')
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        NFA.copy(self.nfa)
        validate.assert_called_once_with()

    def test_nfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_nfa = self.nfa.copy()
        self.assertTrue(self.nfa == new_nfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_nfa = self.nfa.copy()
        new_nfa.final_states.add('q2')
        self.assertTrue(self.nfa != new_nfa, 'NFAs are equal')

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate()

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q3'}
            self.nfa.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.nfa.initial_state = 'q3'
            self.nfa.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            del self.nfa.transitions[self.nfa.initial_state]
            self.nfa.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.nfa.final_states = {'q3'}
            self.nfa.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.nfa.final_states = {3}
            self.nfa.validate()

    def test_read_input_accepted(self):
        """Should return correct states if acceptable NFA input is given."""
        self.assertEqual(self.nfa.read_input('aba'), {'q1', 'q2'})

    def test_validate_missing_state(self):
        """Should silently ignore states without transitions defined."""
        self.nfa.states.add('q3')
        self.nfa.transitions['q0']['a'].add('q3')
        self.assertEqual(self.nfa.validate(), True)

    def test_read_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input('abba')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input('abc')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise('aba')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(list(validation_generator), [
            {'q0'}, {'q1', 'q2'}, {'q0'}, {'q1', 'q2'}
        ])

    def test_accepts_input_true(self):
        """Should return True if NFA input is accepted."""
        self.assertEqual(self.nfa.accepts_input('aba'), True)

    def test_accepts_input_false(self):
        """Should return False if NFA input is rejected."""
        self.assertEqual(self.nfa.accepts_input('abba'), False)

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
        self.assertEqual(nfa.read_input(''), {'q0', 'q1', 'q3'})
        self.assertEqual(nfa.read_input('a'), {'q0', 'q1', 'q2', 'q3'})

    def test_non_str_states(self):
        """should handle non-string state names"""
        nfa = NFA(
            states={0},
            input_symbols={0},
            transitions={0: {}},
            initial_state=0,
            final_states=set())
        # We don't care what the output is, just as long as no exception is
        # raised
        self.assertNotEqual(nfa.accepts_input(''), None)

    def test_operations_other_type(self):
        """Should raise NotImplementedError for concatenate."""
        nfa = NFA(
                states={'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                transitions={'q1': {'0': {'q1'}, '1': {'q1', 'q2'}},
                             'q2': {'': {'q2'}, '0': {'q2'}},
                             'q3': {'1': {'q4'}},
                             'q4': {'0': {'q4'}, '1': {'q4'}}},
                initial_state='q1',
                final_states={'q2', 'q4'})
        other = 42
        with self.assertRaises(NotImplementedError):
            nfa + other

    def test_concatenate(self):
        nfa_a = NFA(
            states={'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q1': {'0': {'q1'}, '1': {'q1', 'q2'}},
                'q2': {'': {'q2'}, '0': {'q2'}},
                'q3': {'1': {'q4'}},
                'q4': {'0': {'q4'}, '1': {'q4'}}
            },
            initial_state='q1',
            final_states={'q2', 'q4'}
        )

        nfa_b = NFA(
            states={'r1', 'r2', 'r3'},
            input_symbols={'0', '1'},
            transitions={
                'r1': {'': {'r3'}, '1': {'r2'}},
                'r2': {'0': {'r2', 'r3'}, '1': {'r3'}},
                'r3': {'0': {'r1'}}
            },
            initial_state='r1',
            final_states={'r1'}
        )

        concat_nfa = nfa_a + nfa_b

        self.assertEqual(concat_nfa.accepts_input(''), False)
        self.assertEqual(concat_nfa.accepts_input('0'), False)
        self.assertEqual(concat_nfa.accepts_input('1'), True)
        self.assertEqual(concat_nfa.accepts_input('00'), False)
        self.assertEqual(concat_nfa.accepts_input('01'), True)
        self.assertEqual(concat_nfa.accepts_input('10'), True)
        self.assertEqual(concat_nfa.accepts_input('11'), True)
        self.assertEqual(concat_nfa.accepts_input('101'), True)
        self.assertEqual(concat_nfa.accepts_input('101100'), True)
        self.assertEqual(concat_nfa.accepts_input('1010'), True)

    def test_kleene_star(self):
        # This NFA accepts aa and ab
        nfa = NFA(
            states={0, 1, 2, 3, 4, 6},
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1, 3}},
                1: {'b': {2}},
                2: {},
                3: {'a': {4}},
                4: {'': {6}},
                6: {}
            },
            initial_state=0,
            final_states={2, 4, 6}
        )
        # This NFA should then accept any number of repetitions
        # of aa or ab concatenated together.
        kleene_nfa = nfa.kleene_star()
        self.assertEqual(kleene_nfa.accepts_input(''), True)
        self.assertEqual(kleene_nfa.accepts_input('a'), False)
        self.assertEqual(kleene_nfa.accepts_input('b'), False)
        self.assertEqual(kleene_nfa.accepts_input('aa'), True)
        self.assertEqual(kleene_nfa.accepts_input('ab'), True)
        self.assertEqual(kleene_nfa.accepts_input('ba'), False)
        self.assertEqual(kleene_nfa.accepts_input('bb'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaa'), False)
        self.assertEqual(kleene_nfa.accepts_input('aba'), False)
        self.assertEqual(kleene_nfa.accepts_input('abaa'), True)
        self.assertEqual(kleene_nfa.accepts_input('abba'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaa'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaab'), True)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaba'), False)

    def test_reverse(self):
        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1}},
                1: {'a': {2}, 'b': {1, 2}},
                2: {},
                3: {'a': {2}, 'b': {2}}
            },
            initial_state=0,
            final_states={2}
        )
        reverse_nfa = reversed(nfa)
        self.assertEqual(reverse_nfa.accepts_input('a'), False)
        self.assertEqual(reverse_nfa.accepts_input('ab'), False)
        self.assertEqual(reverse_nfa.accepts_input('ba'), True)
        self.assertEqual(reverse_nfa.accepts_input('bba'), True)
        self.assertEqual(reverse_nfa.accepts_input('bbba'), True)
