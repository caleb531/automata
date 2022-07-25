#!/usr/bin/env python3
"""Classes and functions for testing the behavior of both DFAs and NFAs."""

import unittest

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata.fa.gnfa import GNFA


class TestFA(unittest.TestCase):
    """A test class for testing all finite automata."""

    def setUp(self):
        """Reset test automata before every test function."""
        # DFA which matches all binary strings ending in an odd number of '1's
        self.dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        # NFA which matches strings beginning with 'a', ending with 'a', and
        # containing no consecutive 'b's
        self.nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}},
                'q1': {'a': {'q1'}, '': {'q2'}},
                'q2': {'b': {'q0'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        # GNFA which matches strings beginning with 'a', ending with 'a', and containing
        # no consecutive 'b's
        self.gnfa = GNFA(
            states={'q_in', 'q_f', 'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'q1': 'a', 'q_f': None, 'q2': None, 'q0': None},
                'q1': {'q1': 'a', 'q2': '', 'q_f': '', 'q0': None},
                'q2': {'q0': 'b', 'q_f': None, 'q2': None, 'q1': None},
                'q_in': {'q0': '', 'q_f': None, 'q2': None, 'q1': None}
            },
            initial_state='q_in',
            final_state='q_f'
        )

    def assert_is_copy(self, first, second):
        """Assert that the first FA is a deep copy of the second."""
        self.assertIsNot(first.states, second.states)
        self.assertEqual(first.states, second.states)
        self.assertIsNot(first.input_symbols, second.input_symbols)
        self.assertEqual(first.input_symbols, second.input_symbols)
        self.assertIsNot(first.transitions, second.transitions)
        self.assertEqual(first.transitions, second.transitions)
        self.assertEqual(first.initial_state, second.initial_state)
        self.assertIsNot(first.final_states, second.final_states)
        self.assertEqual(first.final_states, second.final_states)

    def assert_is_copy_for_gnfa(self, first, second):
        """Assert that the first GNFA is a deep copy of the second."""
        self.assertIsNot(first.states, second.states)
        self.assertEqual(first.states, second.states)
        self.assertIsNot(first.input_symbols, second.input_symbols)
        self.assertEqual(first.input_symbols, second.input_symbols)
        self.assertIsNot(first.transitions, second.transitions)
        self.assertEqual(first.transitions, second.transitions)
        self.assertEqual(first.initial_state, second.initial_state)
        self.assertEqual(first.final_state, second.final_state)
