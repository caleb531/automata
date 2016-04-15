#!/usr/bin/env python3
"""Classes and functions for testing the behavior of both DFAs and NFAs."""

import nose.tools as nose

from automata.dfa import DFA
from automata.nfa import NFA


class TestAutomaton(object):
    """A test class for testing all finite automata."""

    def setup(self):
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

    def assert_is_copy(self, first, second):
        """Assert that the first automaton is an exact copy of the second."""
        nose.assert_is_not(first.states, second.states)
        nose.assert_equal(first.states, second.states)
        nose.assert_is_not(first.input_symbols, second.input_symbols)
        nose.assert_equal(first.input_symbols, second.input_symbols)
        nose.assert_is_not(first.transitions, second.transitions)
        nose.assert_equal(first.transitions, second.transitions)
        nose.assert_equal(first.initial_state, second.initial_state)
        nose.assert_is_not(first.final_states, second.final_states)
        nose.assert_equal(first.final_states, second.final_states)
