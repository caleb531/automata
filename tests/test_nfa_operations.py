#!/usr/bin/env python3
"""Classes and functions for testing NFA operations."""

import nose.tools as nose

import tests.test_automaton as test_automaton
from automata.nfa import NFA


class TestNFAOperations(test_automaton.TestAutomaton):
    """A test class for testing deterministic finite automata operations."""

    def setup(self):
        """Reset test NFAs before every test function."""
        self.nfa1 = NFA(
            states={'c0', 'c1', 'c2', 'c3'},
            symbols={'c', 'a', 't'},
            transitions={
                'c0': {'c': {'c1'}},
                'c1': {'a': {'c2'}},
                'c2': {'t': {'c3'}},
                'c3': {},
            },
            initial_state='c0',
            final_states={'c3'}
        )
        self.nfa2 = NFA(
            states={'d0', 'd1', 'd2', 'd3'},
            symbols={'d', 'o', 'g'},
            transitions={
                'd0': {'d': {'d1'}},
                'd1': {'o': {'d2'}},
                'd2': {'g': {'d3'}},
                'd3': {},
            },
            initial_state='d0',
            final_states={'d3'}
        )
        self.union_states = {
            '{c0,d0}', 'c0', 'c1', 'c2', 'c3', 'd0', 'd1', 'd2', 'd3'}
        self.union_symbols = {'c', 'a', 't', 'd', 'o', 'g'}
        self.union_transitions = {
            '{c0,d0}': {'': {'c0', 'd0'}},
            'c0': {'c': {'c1'}},
            'c1': {'a': {'c2'}},
            'c2': {'t': {'c3'}},
            'c3': {},
            'd0': {'d': {'d1'}},
            'd1': {'o': {'d2'}},
            'd2': {'g': {'d3'}},
            'd3': {},
        }
        self.union_initial_state = '{c0,d0}'
        self.union_final_states = {'c3', 'd3'}

    def test_complement(self):
        """Should compute complement of an NFA."""
        nfa_comp = ~self.nfa1
        nose.assert_equal(nfa_comp.states, self.nfa1.states)
        nose.assert_equal(nfa_comp.symbols, self.nfa1.symbols)
        nose.assert_equal(nfa_comp.transitions, self.nfa1.transitions)
        nose.assert_equal(nfa_comp.initial_state, self.nfa1.initial_state)
        nose.assert_equal(
            nfa_comp.final_states, self.nfa1.states - self.nfa1.final_states)

    def test_union(self):
        """Should compute union of two NFAs."""
        union = self.nfa1 | self.nfa2
        nose.assert_equal(union.states, self.union_states)
        nose.assert_equal(union.symbols, self.union_symbols)
        nose.assert_equal(union.transitions, self.union_transitions)
        nose.assert_equal(union.initial_state, self.union_initial_state)
        nose.assert_equal(union.final_states, {'d3', 'c3'})
