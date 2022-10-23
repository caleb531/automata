#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import os
import os.path
import tempfile
import types
from itertools import product
from unittest.mock import patch

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestDFA(test_fa.TestFA):
    """A test class for testing deterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_dfa(self):
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = DFA.copy(self.dfa)
        self.assertIsNot(new_dfa, self.dfa)

    def test_init_dfa_missing_formal_params(self):
        """Should raise an error if formal DFA parameters are missing."""
        with self.assertRaises(TypeError):
            DFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_dfa(self):
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assertIsNot(new_dfa, self.dfa)

    def test_dfa_immutable_attr_set(self):
        with self.assertRaises(AttributeError):
            self.dfa.states = {}

    def test_dfa_immutable_attr_del(self):
        with self.assertRaises(AttributeError):
            del self.dfa.states

    @patch('automata.fa.dfa.DFA.validate')
    def test_init_validation(self, validate):
        """Should validate DFA when initialized."""
        DFA.copy(self.dfa)
        validate.assert_called_once_with()

    def test_dfa_equal(self):
        """Should correctly determine if two DFAs are equal."""
        new_dfa = self.dfa.copy()
        self.assertTrue(self.dfa == new_dfa, 'DFAs are not equal')

    def test_dfa_not_equal(self):
        """Should correctly determine if two DFAs are not equal."""
        new_dfa = DFA(
            states={'q0'},
            input_symbols={'a'},
            transitions={
                'q0': {'a': 'q0'}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        self.assertTrue(self.dfa != new_dfa, 'DFAs are equal')

    def test_validate_missing_state(self):
        """Should raise error if a state has no transitions defined."""
        with self.assertRaises(exceptions.MissingStateError):
            DFA(
                states={'q0', 'q1'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q0'}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_missing_symbol(self):
        """Should raise error if a symbol transition is missing."""
        with self.assertRaises(exceptions.MissingSymbolError):
            DFA(
                states={'q0'},
                input_symbols={'a', 'b'},
                transitions={
                    'q0': {'a': 'q0'}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q0', 'b': 'q0'}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q1'}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q1'}
                },
                initial_state='q1',
                final_states={'q0'}
            )

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q1'}
                },
                initial_state='q0',
                final_states={'q1'}
            )

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            DFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': 'q1'}
                },
                initial_state='q0',
                final_states={3}
            )

    def test_read_input_accepted(self):
        """Should return correct state if acceptable DFA input is given."""
        self.assertEqual(self.dfa.read_input('0111'), 'q1')

    def test_read_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input('011')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.dfa.read_input('01112')

    def test_accepts_input_true(self):
        """Should return True if DFA input is accepted."""
        self.assertEqual(self.dfa.accepts_input('0111'), True)

    def test_accepts_input_false(self):
        """Should return False if DFA input is rejected."""
        self.assertEqual(self.dfa.accepts_input('011'), False)

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dfa.read_input_stepwise('0111')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(list(validation_generator), [
            'q0', 'q0', 'q1', 'q2', 'q1'
        ])

    def test_operations_other_types(self):
        """Should raise NotImplementedError for all but equals."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        other = 42
        self.assertNotEqual(dfa, other)
        with self.assertRaises(NotImplementedError):
            dfa | other
        with self.assertRaises(NotImplementedError):
            dfa & other
        with self.assertRaises(NotImplementedError):
            dfa - other
        with self.assertRaises(NotImplementedError):
            dfa ^ other
        with self.assertRaises(NotImplementedError):
            dfa < other
        with self.assertRaises(NotImplementedError):
            dfa <= other
        with self.assertRaises(NotImplementedError):
            dfa > other
        with self.assertRaises(NotImplementedError):
            dfa >= other

    def test_equivalence_not_equal(self):
        """Should not be equal."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        self.assertNotEqual(no_consecutive_11_dfa, zero_or_one_1_dfa)

    def test_equivalence_minify(self):
        """Should be equivalent after minify."""
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q3', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'},
                'q3': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q3'}
        )
        minimal_dfa = no_consecutive_11_dfa.minify()
        self.assertEqual(no_consecutive_11_dfa, minimal_dfa)

    def test_equivalence_two_non_minimal(self):
        """Should be equivalent even though they are non minimal."""
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q3', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'},
                'q3': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q3'}
        )
        other_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q2'},
                'q3': {'0': 'q3', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        self.assertEqual(no_consecutive_11_dfa, other_dfa)

    def test_complement(self):
        """Should compute the complement of a DFA"""
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        complement_dfa = ~no_consecutive_11_dfa
        self.assertEqual(complement_dfa.states, no_consecutive_11_dfa.states)
        self.assertEqual(
            complement_dfa.input_symbols, no_consecutive_11_dfa.input_symbols
        )
        self.assertEqual(
            complement_dfa.transitions, no_consecutive_11_dfa.transitions
        )
        self.assertEqual(
            complement_dfa.initial_state, no_consecutive_11_dfa.initial_state
        )
        self.assertEqual(
            complement_dfa.final_states, {'q2'}
        )

    def test_union(self):
        """Should compute the union between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.union(B, retain_names=True, minify=False)
        self.assertEqual(new_dfa.states, {
            ('q0', 'p0'), ('q0', 'p1'), ('q0', 'p2'),
            ('q1', 'p0'), ('q1', 'p1'), ('q1', 'p2'),
            ('q2', 'p0'), ('q2', 'p1'), ('q2', 'p2'),
            ('q3', 'p0'), ('q3', 'p1'), ('q3', 'p2'),
            ('q4', 'p0'), ('q4', 'p1'), ('q4', 'p2')
        })
        self.assertEqual(new_dfa.input_symbols, {'0', '1'})
        self.assertEqual(new_dfa.transitions, {
            ('q0', 'p0'): {'0': ('q0', 'p0'), '1': ('q1', 'p1')},
            ('q0', 'p1'): {'0': ('q0', 'p0'), '1': ('q1', 'p2')},
            ('q0', 'p2'): {'0': ('q0', 'p2'), '1': ('q1', 'p2')},
            ('q1', 'p0'): {'0': ('q1', 'p0'), '1': ('q2', 'p1')},
            ('q1', 'p1'): {'0': ('q1', 'p0'), '1': ('q2', 'p2')},
            ('q1', 'p2'): {'0': ('q1', 'p2'), '1': ('q2', 'p2')},
            ('q2', 'p0'): {'0': ('q2', 'p0'), '1': ('q3', 'p1')},
            ('q2', 'p1'): {'0': ('q2', 'p0'), '1': ('q3', 'p2')},
            ('q2', 'p2'): {'0': ('q2', 'p2'), '1': ('q3', 'p2')},
            ('q3', 'p0'): {'0': ('q3', 'p0'), '1': ('q4', 'p1')},
            ('q3', 'p1'): {'0': ('q3', 'p0'), '1': ('q4', 'p2')},
            ('q3', 'p2'): {'0': ('q3', 'p2'), '1': ('q4', 'p2')},
            ('q4', 'p0'): {'0': ('q4', 'p0'), '1': ('q4', 'p1')},
            ('q4', 'p1'): {'0': ('q4', 'p0'), '1': ('q4', 'p2')},
            ('q4', 'p2'): {'0': ('q4', 'p2'), '1': ('q4', 'p2')}
        })
        self.assertEqual(new_dfa.initial_state, ('q0', 'p0'))
        self.assertEqual(new_dfa.final_states, {
            ('q0', 'p0'), ('q0', 'p1'),
            ('q1', 'p0'), ('q1', 'p1'),
            ('q2', 'p0'), ('q2', 'p1'),
            ('q3', 'p0'), ('q3', 'p1'),
            ('q4', 'p0'), ('q4', 'p1'), ('q4', 'p2')
        })

    def test_intersection(self):
        """Should compute the intersection between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.intersection(B, retain_names=True, minify=False)
        self.assertEqual(new_dfa.states, {
            ('q0', 'p0'), ('q0', 'p1'), ('q0', 'p2'),
            ('q1', 'p0'), ('q1', 'p1'), ('q1', 'p2'),
            ('q2', 'p0'), ('q2', 'p1'), ('q2', 'p2'),
            ('q3', 'p0'), ('q3', 'p1'), ('q3', 'p2'),
            ('q4', 'p0'), ('q4', 'p1'), ('q4', 'p2')
        })
        self.assertEqual(new_dfa.input_symbols, {'0', '1'})
        self.assertEqual(new_dfa.transitions, {
            ('q0', 'p0'): {'0': ('q0', 'p0'), '1': ('q1', 'p1')},
            ('q0', 'p1'): {'0': ('q0', 'p0'), '1': ('q1', 'p2')},
            ('q0', 'p2'): {'0': ('q0', 'p2'), '1': ('q1', 'p2')},
            ('q1', 'p0'): {'0': ('q1', 'p0'), '1': ('q2', 'p1')},
            ('q1', 'p1'): {'0': ('q1', 'p0'), '1': ('q2', 'p2')},
            ('q1', 'p2'): {'0': ('q1', 'p2'), '1': ('q2', 'p2')},
            ('q2', 'p0'): {'0': ('q2', 'p0'), '1': ('q3', 'p1')},
            ('q2', 'p1'): {'0': ('q2', 'p0'), '1': ('q3', 'p2')},
            ('q2', 'p2'): {'0': ('q2', 'p2'), '1': ('q3', 'p2')},
            ('q3', 'p0'): {'0': ('q3', 'p0'), '1': ('q4', 'p1')},
            ('q3', 'p1'): {'0': ('q3', 'p0'), '1': ('q4', 'p2')},
            ('q3', 'p2'): {'0': ('q3', 'p2'), '1': ('q4', 'p2')},
            ('q4', 'p0'): {'0': ('q4', 'p0'), '1': ('q4', 'p1')},
            ('q4', 'p1'): {'0': ('q4', 'p0'), '1': ('q4', 'p2')},
            ('q4', 'p2'): {'0': ('q4', 'p2'), '1': ('q4', 'p2')}
        })
        self.assertEqual(new_dfa.initial_state, ('q0', 'p0'))
        self.assertEqual(new_dfa.final_states, {
            ('q4', 'p0'), ('q4', 'p1'),
        })

    def test_difference(self):
        """Should compute the difference between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.difference(B, retain_names=True, minify=False)
        self.assertEqual(new_dfa.states, {
            ('q0', 'p0'), ('q0', 'p1'), ('q0', 'p2'),
            ('q1', 'p0'), ('q1', 'p1'), ('q1', 'p2'),
            ('q2', 'p0'), ('q2', 'p1'), ('q2', 'p2'),
            ('q3', 'p0'), ('q3', 'p1'), ('q3', 'p2'),
            ('q4', 'p0'), ('q4', 'p1'), ('q4', 'p2')
        })
        self.assertEqual(new_dfa.input_symbols, {'0', '1'})
        self.assertEqual(new_dfa.transitions, {
            ('q0', 'p0'): {'0': ('q0', 'p0'), '1': ('q1', 'p1')},
            ('q0', 'p1'): {'0': ('q0', 'p0'), '1': ('q1', 'p2')},
            ('q0', 'p2'): {'0': ('q0', 'p2'), '1': ('q1', 'p2')},
            ('q1', 'p0'): {'0': ('q1', 'p0'), '1': ('q2', 'p1')},
            ('q1', 'p1'): {'0': ('q1', 'p0'), '1': ('q2', 'p2')},
            ('q1', 'p2'): {'0': ('q1', 'p2'), '1': ('q2', 'p2')},
            ('q2', 'p0'): {'0': ('q2', 'p0'), '1': ('q3', 'p1')},
            ('q2', 'p1'): {'0': ('q2', 'p0'), '1': ('q3', 'p2')},
            ('q2', 'p2'): {'0': ('q2', 'p2'), '1': ('q3', 'p2')},
            ('q3', 'p0'): {'0': ('q3', 'p0'), '1': ('q4', 'p1')},
            ('q3', 'p1'): {'0': ('q3', 'p0'), '1': ('q4', 'p2')},
            ('q3', 'p2'): {'0': ('q3', 'p2'), '1': ('q4', 'p2')},
            ('q4', 'p0'): {'0': ('q4', 'p0'), '1': ('q4', 'p1')},
            ('q4', 'p1'): {'0': ('q4', 'p0'), '1': ('q4', 'p2')},
            ('q4', 'p2'): {'0': ('q4', 'p2'), '1': ('q4', 'p2')}
        })
        self.assertEqual(new_dfa.initial_state, ('q0', 'p0'))
        self.assertEqual(new_dfa.final_states, {
             ('q4', 'p2')
        })

    def test_symmetric_difference(self):
        """Should compute the symmetric difference between two DFAs"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.symmetric_difference(B, retain_names=True, minify=False)
        self.assertEqual(new_dfa.states, {
            ('q0', 'p0'), ('q0', 'p1'), ('q0', 'p2'),
            ('q1', 'p0'), ('q1', 'p1'), ('q1', 'p2'),
            ('q2', 'p0'), ('q2', 'p1'), ('q2', 'p2'),
            ('q3', 'p0'), ('q3', 'p1'), ('q3', 'p2'),
            ('q4', 'p0'), ('q4', 'p1'), ('q4', 'p2')
        })
        self.assertEqual(new_dfa.input_symbols, {'0', '1'})
        self.assertEqual(new_dfa.transitions, {
            ('q0', 'p0'): {'0': ('q0', 'p0'), '1': ('q1', 'p1')},
            ('q0', 'p1'): {'0': ('q0', 'p0'), '1': ('q1', 'p2')},
            ('q0', 'p2'): {'0': ('q0', 'p2'), '1': ('q1', 'p2')},
            ('q1', 'p0'): {'0': ('q1', 'p0'), '1': ('q2', 'p1')},
            ('q1', 'p1'): {'0': ('q1', 'p0'), '1': ('q2', 'p2')},
            ('q1', 'p2'): {'0': ('q1', 'p2'), '1': ('q2', 'p2')},
            ('q2', 'p0'): {'0': ('q2', 'p0'), '1': ('q3', 'p1')},
            ('q2', 'p1'): {'0': ('q2', 'p0'), '1': ('q3', 'p2')},
            ('q2', 'p2'): {'0': ('q2', 'p2'), '1': ('q3', 'p2')},
            ('q3', 'p0'): {'0': ('q3', 'p0'), '1': ('q4', 'p1')},
            ('q3', 'p1'): {'0': ('q3', 'p0'), '1': ('q4', 'p2')},
            ('q3', 'p2'): {'0': ('q3', 'p2'), '1': ('q4', 'p2')},
            ('q4', 'p0'): {'0': ('q4', 'p0'), '1': ('q4', 'p1')},
            ('q4', 'p1'): {'0': ('q4', 'p0'), '1': ('q4', 'p2')},
            ('q4', 'p2'): {'0': ('q4', 'p2'), '1': ('q4', 'p2')}
        })
        self.assertEqual(new_dfa.initial_state, ('q0', 'p0'))
        self.assertEqual(new_dfa.final_states, {
            ('q0', 'p0'), ('q0', 'p1'),
            ('q1', 'p0'), ('q1', 'p1'),
            ('q2', 'p0'), ('q2', 'p1'),
            ('q3', 'p0'), ('q3', 'p1'),
            ('q4', 'p2')
        })

    def test_issubset(self):
        """Should test if one DFA is a subset of another"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # Test both proper subset and subset with each set as left hand side
        self.assertTrue(zero_or_one_1_dfa < no_consecutive_11_dfa)
        self.assertTrue(zero_or_one_1_dfa <= no_consecutive_11_dfa)
        self.assertFalse(no_consecutive_11_dfa < zero_or_one_1_dfa)
        self.assertFalse(no_consecutive_11_dfa <= zero_or_one_1_dfa)

    def test_issuperset(self):
        """Should test if one DFA is a superset of another"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # Test both proper subset and subset with each set as left hand side
        self.assertFalse(zero_or_one_1_dfa > no_consecutive_11_dfa)
        self.assertFalse(zero_or_one_1_dfa >= no_consecutive_11_dfa)
        self.assertTrue(no_consecutive_11_dfa > zero_or_one_1_dfa)
        self.assertTrue(no_consecutive_11_dfa >= zero_or_one_1_dfa)

    def test_symbol_mismatch(self):
        """Should test if symbol mismatch is raised"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of b
        zero_or_one_b_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q0', 'b': 'q1'},
                'q1': {'a': 'q1', 'b': 'q2'},
                'q2': {'a': 'q2', 'b': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.issubset(no_consecutive_11_dfa)

        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.difference(no_consecutive_11_dfa)

    def test_isdisjoint(self):
        """Should test if two DFAs are disjoint"""
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q3'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        B = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain at least
        # one occurrence of 1
        C = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q1'},
            },
            initial_state='q0',
            final_states={'q1'}
        )
        self.assertTrue(A.isdisjoint(B))
        self.assertTrue(B.isdisjoint(A))
        self.assertFalse(A.isdisjoint(C))
        self.assertFalse(B.isdisjoint(C))

    def test_isempty_non_empty(self):
        """Should test if a non-empty DFA is empty"""
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q3'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        self.assertFalse(A.isempty())

    def test_isempty_empty(self):
        """Should test if an empty DFA is empty"""
        # This DFA has no reachable final states and
        # therefore accepts the empty language
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q0', '1': 'q1'},
                'q3': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        self.assertTrue(A.isempty())

    def test_isfinite_infinite(self):
        """Should test if an infinite DFA is finite (case #1)"""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        self.assertFalse(A.isfinite())

    def test_isfinite_infinite_case_2(self):
        """Should test if an infinite DFA is finite (case #2)"""
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q2', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q3'},
                'q3': {'0': 'q4', '1': 'q4'},
                'q4': {'0': 'q5', '1': 'q5'},
                'q5': {'0': 'q6', '1': 'q6'},
                'q6': {'0': 'q6', '1': 'q6'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'}
        )
        self.assertFalse(A.isfinite())

    def test_isfinite_finite(self):
        """Should test if a finite DFA is finite"""
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q2', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q3'},
                'q3': {'0': 'q4', '1': 'q4'},
                'q4': {'0': 'q5', '1': 'q5'},
                'q5': {'0': 'q6', '1': 'q6'},
                'q6': {'0': 'q6', '1': 'q6'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}
        )
        self.assertTrue(A.isfinite())

    def test_isfinite_empty(self):
        """Should test if an empty DFA is finite"""
        # This DFA has no reachable final states and
        # therefore is finite.
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q0', '1': 'q1'},
                'q3': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        self.assertTrue(A.isfinite())

    def test_isfinite_universe(self):
        # This DFA accepts all binary strings and
        # therefore is infinite.
        A = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states={'q0'}
        )
        self.assertFalse(A.isfinite())

    def test_set_laws(self):
        """Tests many set laws that are true for all sets"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        # This DFA accepts all binary strings
        U = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        # This DFA represents the empty language
        empty = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'}
            },
            initial_state='q0',
            final_states=set()
        )
        # De Morgan's laws
        self.assertEqual(~(A | B), ~A & ~B)
        self.assertEqual(~(A & B), ~A | ~B)
        # Complement laws
        self.assertEqual(A | ~A, U)
        self.assertEqual(A & ~A, empty)
        self.assertEqual(~U, empty)
        self.assertEqual(~empty, U)
        # Involution
        self.assertEqual(A, ~(~A))
        # Relationships between relative and absolute complements
        self.assertEqual(A - B, A & ~B)
        self.assertEqual(~(A - B), ~A | B)
        self.assertEqual(~(A - B), ~A | (B & A))
        # Relationship with set difference
        self.assertEqual(~A - ~B, B - A)
        # Symmetric difference
        self.assertEqual(A ^ B, (A - B) | (B - A))
        self.assertEqual(A ^ B, (A | B) - (A & B))
        # Commutativity
        self.assertEqual(A | B, B | A)
        self.assertEqual(A & B, B & A)
        self.assertEqual(A ^ B, B ^ A)

    def test_minify_dfa(self):
        """Should minify a given DFA."""
        # This DFA accepts all words which are at least two characters long.
        # The states q1/q2 and q3/q4/q5/q6 are redundant.
        # The state q7 is not reachable.
        dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q2'},
                'q1': {'0': 'q3', '1': 'q4'},
                'q2': {'0': 'q5', '1': 'q6'},
                'q3': {'0': 'q3', '1': 'q3'},
                'q4': {'0': 'q4', '1': 'q4'},
                'q5': {'0': 'q5', '1': 'q5'},
                'q6': {'0': 'q6', '1': 'q6'},
                'q7': {'0': 'q7', '1': 'q7'}
            },
            initial_state='q0',
            final_states={'q3', 'q4', 'q5', 'q6'}
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {
            frozenset(('q0',)), frozenset(('q1', 'q2')), frozenset(('q3', 'q4', 'q5', 'q6'))
        })
        self.assertEqual(minimal_dfa.input_symbols, {'0', '1'})
        self.assertEqual(minimal_dfa.transitions, {
            frozenset(('q0',)): {
                '0': frozenset(('q1', 'q2')), '1': frozenset(('q1', 'q2'))
            },
            frozenset(('q1', 'q2')): {
                '0': frozenset(('q3', 'q4', 'q5', 'q6')), '1': frozenset(('q3', 'q4', 'q5', 'q6'))
            },
            frozenset(('q3', 'q4', 'q5', 'q6')): {
                '0': frozenset(('q3', 'q4', 'q5', 'q6')), '1': frozenset(('q3', 'q4', 'q5', 'q6'))
            }
        })
        self.assertEqual(minimal_dfa.initial_state, frozenset(('q0',)))
        self.assertEqual(minimal_dfa.final_states, {frozenset(('q3', 'q4', 'q5', 'q6'))})

    def test_minify_dfa_complex(self):
        """Should minify a given large DFA."""
        dfa = DFA(
            states={'13', '56', '18', '10', '15', '26', '24', '54', '32', '27',
                    '5', '43', '8', '3', '17', '45', '57', '46', '35', '9',
                    '0', '21', '39', '51', '6', '55', '47', '11', '20', '12',
                    '59', '38', '44', '52', '16', '41', '1', '4', '28', '58',
                    '48', '23', '22', '2', '31', '36', '34', '49', '40', '7',
                    '25', '30', '53', '42', '33', '19', '50', '37', '14',
                    '29'},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={'55': {'L': '20', 'U': '49', 'R': '20', 'D': '49'},
                         '57': {'L': '5', 'U': '6', 'R': '1', 'D': '46'},
                         '35': {'L': '44', 'U': '32', 'R': '36', 'D': '33'},
                         '13': {'L': '45', 'U': '23', 'R': '45', 'D': '23'},
                         '43': {'L': '44', 'U': '32', 'R': '44', 'D': '33'},
                         '9': {'L': '5', 'U': '6', 'R': '1', 'D': '6'},
                         '53': {'L': '20', 'U': '33', 'R': '20', 'D': '32'},
                         '12': {'L': '40', 'U': '23', 'R': '25', 'D': '11'},
                         '42': {'L': '1', 'U': '49', 'R': '5', 'D': '49'},
                         '24': {'L': '40', 'U': '48', 'R': '25', 'D': '23'},
                         '27': {'L': '5', 'U': '46', 'R': '1', 'D': '6'},
                         '22': {'L': '40', 'U': '48', 'R': '25', 'D': '11'},
                         '19': {'L': '36', 'U': '32', 'R': '44', 'D': '33'},
                         '59': {'L': '40', 'U': '48', 'R': '45', 'D': '11'},
                         '39': {'L': '45', 'U': '48', 'R': '25', 'D': '11'},
                         '51': {'L': '20', 'U': '18', 'R': '20', 'D': '18'},
                         '34': {'L': '5', 'U': '4', 'R': '1', 'D': '31'},
                         '33': {'L': '44', 'U': '0', 'R': '36', 'D': '28'},
                         '23': {'L': '45', 'U': '8', 'R': '45', 'D': '8'},
                         '46': {'L': '44', 'U': '0', 'R': '44', 'D': '28'},
                         '58': {'L': '5', 'U': '4', 'R': '1', 'D': '4'},
                         '50': {'L': '20', 'U': '28', 'R': '20', 'D': '0'},
                         '54': {'L': '40', 'U': '8', 'R': '25', 'D': '41'},
                         '49': {'L': '1', 'U': '18', 'R': '5', 'D': '18'},
                         '21': {'L': '40', 'U': '26', 'R': '25', 'D': '8'},
                         '16': {'L': '5', 'U': '31', 'R': '1', 'D': '4'},
                         '6': {'L': '40', 'U': '26', 'R': '25', 'D': '41'},
                         '32': {'L': '36', 'U': '0', 'R': '44', 'D': '28'},
                         '48': {'L': '40', 'U': '26', 'R': '45', 'D': '41'},
                         '11': {'L': '45', 'U': '26', 'R': '25', 'D': '41'},
                         '15': {'L': '14', 'U': '49', 'R': '14', 'D': '49'},
                         '1': {'L': '56', 'U': '6', 'R': '37', 'D': '46'},
                         '3': {'L': '4', 'U': '32', 'R': '17', 'D': '33'},
                         '45': {'L': '8', 'U': '23', 'R': '8', 'D': '23'},
                         '52': {'L': '4', 'U': '32', 'R': '4', 'D': '33'},
                         '36': {'L': '56', 'U': '6', 'R': '37', 'D': '6'},
                         '20': {'L': '14', 'U': '33', 'R': '14', 'D': '32'},
                         '25': {'L': '47', 'U': '23', 'R': '10', 'D': '11'},
                         '29': {'L': '37', 'U': '49', 'R': '56', 'D': '49'},
                         '40': {'L': '47', 'U': '48', 'R': '10', 'D': '23'},
                         '5': {'L': '56', 'U': '46', 'R': '37', 'D': '6'},
                         '44': {'L': '47', 'U': '48', 'R': '10', 'D': '11'},
                         '38': {'L': '17', 'U': '32', 'R': '4', 'D': '33'},
                         '2': {'L': '47', 'U': '48', 'R': '8', 'D': '11'},
                         '30': {'L': '8', 'U': '48', 'R': '10', 'D': '11'},
                         '7': {'L': '14', 'U': '18', 'R': '14', 'D': '18'},
                         '37': {'L': '56', 'U': '4', 'R': '37', 'D': '31'},
                         '28': {'L': '4', 'U': '0', 'R': '17', 'D': '28'},
                         '8': {'L': '8', 'U': '8', 'R': '8', 'D': '8'},
                         '31': {'L': '4', 'U': '0', 'R': '4', 'D': '28'},
                         '17': {'L': '56', 'U': '4', 'R': '37', 'D': '4'},
                         '14': {'L': '14', 'U': '28', 'R': '14', 'D': '0'},
                         '10': {'L': '47', 'U': '8', 'R': '10', 'D': '41'},
                         '18': {'L': '37', 'U': '18', 'R': '56', 'D': '18'},
                         '47': {'L': '47', 'U': '26', 'R': '10', 'D': '8'},
                         '56': {'L': '56', 'U': '31', 'R': '37', 'D': '4'},
                         '4': {'L': '47', 'U': '26', 'R': '10', 'D': '41'},
                         '0': {'L': '17', 'U': '0', 'R': '4', 'D': '28'},
                         '26': {'L': '47', 'U': '26', 'R': '8', 'D': '41'},
                         '41': {'L': '8', 'U': '26', 'R': '10', 'D': '41'}},
            initial_state='55',
            final_states={'15', '24', '54', '32', '27', '5', '43', '57', '3',
                          '46', '35', '9', '21', '39', '51', '6', '55', '11',
                          '20', '12', '59', '38', '44', '52', '16', '1', '58',
                          '48', '22', '2', '36', '34', '49', '40', '25', '30',
                          '53', '42', '33', '19', '50', '29'})
        large_tuple = ('0', '10', '14', '17', '18', '23', '26', '28', '31', '37', '4', '41', '45', '47', '56', '8')
        check_dfa = DFA(
            states={frozenset(('5',)), frozenset(('36',)), frozenset(('1',)), frozenset(('49',)), frozenset(('40',)),
                    frozenset(('25',)), frozenset(('46',)), frozenset(('6',)), frozenset(('55',)),
                    frozenset(large_tuple),
                    frozenset(('33',)), frozenset(('11',)), frozenset(('20',)), frozenset(('48',)), frozenset(('44',)),
                    frozenset(('32',))},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={
                frozenset(('48',)):
                {'L': frozenset(('40',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(large_tuple),
                 'D': frozenset(large_tuple)},
                frozenset(('44',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('48',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('11',))},
                frozenset(('40',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('48',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(large_tuple)},
                frozenset(('33',)):
                {'L': frozenset(('44',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('36',)),
                 'D': frozenset(large_tuple)},
                frozenset(('55',)): {
                    'L': frozenset(('20',)), 'U': frozenset(('49',)), 'R': frozenset(('20',)), 'D': frozenset(('49',))
                },
                frozenset(('32',)):
                {'L': frozenset(('36',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('44',)),
                 'D': frozenset(large_tuple)},
                frozenset(('46',)):
                {'L': frozenset(('44',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('44',)),
                 'D': frozenset(large_tuple)},
                frozenset(('25',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(large_tuple),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('11',))},
                frozenset(('6',)):
                {'L': frozenset(('40',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('25',)),
                 'D': frozenset(large_tuple)},
                frozenset(('11',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('25',)),
                 'D': frozenset(large_tuple)},
                frozenset(('5',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('46',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('6',))},
                frozenset(('49',)):
                {'L': frozenset(('1',)),
                 'U': frozenset(large_tuple),
                 'R': frozenset(('5',)),
                 'D': frozenset(large_tuple)},
                frozenset(large_tuple):
                {'L': frozenset(large_tuple),
                 'U': frozenset(large_tuple),
                 'R': frozenset(large_tuple),
                 'D': frozenset(large_tuple)},
                frozenset(('20',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('33',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('32',))},
                frozenset(('36',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('6',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('6',))},
                frozenset(('1',)):
                {'L': frozenset(large_tuple),
                 'U': frozenset(('6',)),
                 'R': frozenset(large_tuple),
                 'D': frozenset(('46',))}},
            initial_state=frozenset(('55',)),
            final_states={frozenset(('5',)), frozenset(('1',)), frozenset(('36',)), frozenset(('49',)),
                          frozenset(('40',)), frozenset(('25',)), frozenset(('46',)), frozenset(('6',)),
                          frozenset(('55',)), frozenset(('33',)), frozenset(('11',)), frozenset(('20',)),
                          frozenset(('48',)), frozenset(('44',)), frozenset(('32',))})
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, check_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, check_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, check_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, check_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, check_dfa.final_states)

    def test_minify_minimal_dfa(self):
        """Should minify an already minimal DFA."""
        # This DFA just accepts words ending in 1.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        minimal_dfa = dfa.minify(retain_names=True)
        other_minimal_dfa = DFA(
            states={frozenset(('q0',)), frozenset(('q1',))},
            input_symbols={'0', '1'},
            transitions={
                frozenset(('q0',)): {'0': frozenset(('q0',)), '1': frozenset(('q1',))},
                frozenset(('q1',)): {'0': frozenset(('q0',)), '1': frozenset(('q1',))}
            },
            initial_state=frozenset(('q0',)),
            final_states={frozenset(('q1',))}
        )

        self.assertEqual(minimal_dfa.states, other_minimal_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, other_minimal_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, other_minimal_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, other_minimal_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, other_minimal_dfa.final_states)

    def test_minify_dfa_initial_state(self):
        """Should minify a DFA where the initial state is being changed."""
        # This DFA accepts all words with ones and zeroes.
        # The two states can be merged into one.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states={'q0', 'q1'},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(('q0', 'q1'))})
        self.assertEqual(minimal_dfa.input_symbols, {'0', '1'})
        self.assertEqual(minimal_dfa.transitions, {
            frozenset(('q0', 'q1')): {'0': frozenset(('q0', 'q1')), '1': frozenset(('q0', 'q1'))}
        })
        self.assertEqual(minimal_dfa.initial_state, frozenset(('q0', 'q1')))
        self.assertEqual(minimal_dfa.final_states, {frozenset(('q0', 'q1'))})

    def test_minify_dfa_no_final_states(self):
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states=set(),
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(('q0', 'q1'))})
        self.assertEqual(minimal_dfa.input_symbols, {'0', '1'})
        self.assertEqual(minimal_dfa.transitions, {
            frozenset(('q0', 'q1')): {'0': frozenset(('q0', 'q1')), '1': frozenset(('q0', 'q1'))},
        })
        self.assertEqual(minimal_dfa.initial_state, frozenset(('q0', 'q1')))
        self.assertEqual(minimal_dfa.final_states, set())

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
        dfa = DFA.from_nfa(nfa, retain_names=True)
        self.assertEqual(dfa.states, {frozenset(), frozenset(('q0',)), frozenset(('q0', 'q1')), frozenset(('q2',))})
        self.assertEqual(dfa.input_symbols, {'0', '1'})
        self.assertEqual(dfa.transitions, {
            frozenset(): {'0': frozenset(), '1': frozenset()},
            frozenset(('q0',)): {'0': frozenset(('q0', 'q1')), '1': frozenset()},
            frozenset(('q0', 'q1')): {'0': frozenset(('q0', 'q1')), '1': frozenset(('q2',))},
            frozenset(('q2',)): {'0': frozenset(), '1': frozenset()}
        })
        self.assertEqual(dfa.initial_state, frozenset(('q0',)))
        self.assertEqual(dfa.final_states, {frozenset(('q2',))})

    def test_init_nfa_more_complex(self):
        """Should convert to a DFA a more complex NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}, '1': {'q0'}},
                'q1': {'0': {'q1'}, '1': {'q2'}},
                'q2': {'0': {'q2'}, '1': {'q1'}}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA.from_nfa(nfa, retain_names=True)
        self.assertEqual(dfa.states, {
            frozenset(('q0',)), frozenset(('q0', 'q1')), frozenset(('q0', 'q2')), frozenset(('q0', 'q1', 'q2'))
        })
        self.assertEqual(dfa.input_symbols, {'0', '1'})
        self.assertEqual(dfa.transitions, {
            frozenset(('q0',)): {'1': frozenset(('q0',)), '0': frozenset(('q0', 'q1'))},
            frozenset(('q0', 'q1')): {'1': frozenset(('q0', 'q2')), '0': frozenset(('q0', 'q1'))},
            frozenset(('q0', 'q2')): {'1': frozenset(('q0', 'q1')), '0': frozenset(('q0', 'q1', 'q2'))},
            frozenset(('q0', 'q1', 'q2')): {'1': frozenset(('q0', 'q1', 'q2')), '0': frozenset(('q0', 'q1', 'q2'))}
        })
        self.assertEqual(dfa.initial_state, frozenset(('q0',)))
        self.assertEqual(dfa.final_states, {frozenset(('q0', 'q1', 'q2')), frozenset(('q0', 'q2'))})

    def test_init_nfa_lambda_transition(self):
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA.from_nfa(self.nfa, retain_names=True)
        self.assertEqual(dfa.states, {frozenset(), frozenset(('q0',)), frozenset(('q1', 'q2'))})
        self.assertEqual(dfa.input_symbols, {'a', 'b'})
        self.assertEqual(dfa.transitions, {
            frozenset(): {'a': frozenset(), 'b': frozenset()},
            frozenset(('q0',)): {'a': frozenset(('q1', 'q2')), 'b': frozenset()},
            frozenset(('q1', 'q2')): {'a': frozenset(('q1', 'q2')), 'b': frozenset(('q0',))},
        })
        self.assertEqual(dfa.initial_state, frozenset(('q0',)))
        self.assertEqual(dfa.final_states, {frozenset(('q1', 'q2'))})

    def test_nfa_to_dfa_with_lambda_transitions(self):
        """ Test NFA->DFA when initial state has lambda transitions """
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'': {'q2'}},
                'q1': {'a': {'q1'}},
                'q2': {'a': {'q1'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        dfa = DFA.from_nfa(nfa, retain_names=True)  # returns an equivalent DFA
        self.assertEqual(dfa.read_input('a'), frozenset(('q1',)))

    def test_partial_dfa(self):
        """Should allow for partial DFA when flag is set"""
        dfa = DFA(
            states={'', 'a', 'b', 'aa', 'bb', 'ab', 'ba'},
            input_symbols={'a', 'b'},
            transitions={
                '': {'a': 'a', 'b': 'b'},
                'a': {'b': 'ab', 'a': 'aa'},
                'b': {'b': 'bb'},
                'aa': {'a': 'aa', 'b': 'ab'},
                'bb': {'a': 'ba'},
                'ab': {'b': 'bb'},
                'ba': {'a': 'aa'}
            },
            initial_state='',
            final_states={'aa'},
            allow_partial=True
        )
        self.assertEqual(dfa.read_input('aa'), 'aa')

    def test_show_diagram_initial_final_different(self):
        """
        Should construct the diagram for a DFA whose initial state
        is not a final state.
        """
        graph = self.dfa.show_diagram()
        self.assertEqual(
            {node.get_name() for node in graph.get_nodes()},
            {'q0', 'q1', 'q2'})
        self.assertEqual(graph.get_node('q0')[0].get_style(), 'filled')
        self.assertEqual(graph.get_node('q1')[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q2')[0].get_peripheries(), None)
        self.assertEqual(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', '0', 'q0'),
                ('q0', '1', 'q1'),
                ('q1', '0', 'q0'),
                ('q1', '1', 'q2'),
                ('q2', '0', 'q2'),
                ('q2', '1', 'q1')
            })

    def test_show_diagram_initial_final_same(self):
        """
        Should construct the diagram for a DFA whose initial state
        is also a final state.
        """
        # This DFA accepts all words which do not contain two consecutive
        # occurrences of 1
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        graph = dfa.show_diagram()
        self.assertEqual(
            {node.get_name() for node in graph.get_nodes()},
            {'q0', 'q1', 'q2'})
        self.assertEqual(graph.get_node('q0')[0].get_style(), 'filled')
        self.assertEqual(graph.get_node('q0')[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q1')[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q2')[0].get_peripheries(), None)
        self.assertEqual(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', '0', 'q0'),
                ('q0', '1', 'q1'),
                ('q1', '0', 'q0'),
                ('q1', '1', 'q2'),
                ('q2', '0', 'q2'),
                ('q2', '1', 'q2')
            })

    def test_show_diagram_write_file(self):
        """
        Should construct the diagram for a DFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, 'test_dfa.png')
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.dfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_minimal_finite_language(self):
        """Should compute the minimal DFA accepting the given finite language"""

        # Same language described in the book this algorithm comes from
        language = {'aa', 'aaa', 'aaba', 'aabbb', 'abaa', 'ababb', 'abbab',
                    'baa', 'babb', 'bbaa', 'bbabb', 'bbbab'}

        equiv_dfa = DFA(
            states=set(range(10)),
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': 0, 'b': 0},
                1: {'a': 2, 'b': 3},
                2: {'a': 4, 'b': 5},
                3: {'a': 7, 'b': 5},
                4: {'a': 9, 'b': 7},
                5: {'a': 7, 'b': 6},
                6: {'a': 8, 'b': 0},
                7: {'a': 9, 'b': 8},
                8: {'a': 0, 'b': 9},
                9: {'a': 0, 'b': 0},
            },
            initial_state=1,
            final_states={4, 9}
        )

        minimal_dfa = DFA.from_finite_language(language, {'a', 'b'})

        self.assertEqual(len(minimal_dfa.states), len(equiv_dfa.states))
        self.assertEqual(minimal_dfa, equiv_dfa)

    def test_minimal_finite_language_large(self):
        """Should compute the minimal DFA accepting the given finite language on large test case"""
        m = 50
        n = 50
        language = ['a' * i + 'b' * j for i, j in product(range(n), range(m))]

        equiv_dfa = DFA.from_finite_language(language, {'a', 'b'})
        minimal_dfa = equiv_dfa.minify()

        self.assertEqual(equiv_dfa, minimal_dfa)
        self.assertEqual(len(equiv_dfa.states), len(minimal_dfa.states))
