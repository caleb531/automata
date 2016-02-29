#!/usr/bin/env python3
"""Classes and functions for testing DFA operations."""

import nose.tools as nose

import automata.automaton as automaton
import tests.test_automaton as test_automaton
from automata.dfa import DFA


class TestDFAOperations(test_automaton.TestAutomaton):
    """A test class for testing deterministic finite automata operations."""

    def setup(self):
        """Reset test DFAs before every test function."""
        # DFA which matches strings containing zero or more occurrences of 'a'
        # but only one occurrence of 'b'
        self.dfa1 = DFA(
            states={'q0', 'q1'},
            symbols={'a', 'b'},
            transitions={
                'q0': {'a': 'q0', 'b': 'q1'},
                'q1': {'a': 'q1', 'b': 'q0'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        self.dfa2 = DFA(
            states={'s0', 's1', 's2'},
            symbols={'a', 'b'},
            transitions={
                's0': {'a': 's1', 'b': 's2'},
                's1': {'a': 's2', 'b': 's0'},
                's2': {'a': 's0', 'b': 's1'}
            },
            initial_state='s0',
            final_states={'s2'}
        )

    def test_complement(self):
        """Should compute complement of a DFA."""
        comp = ~self.dfa1
        nose.assert_equal(comp.states, self.dfa1.states)
        nose.assert_equal(comp.symbols, self.dfa1.symbols)
        nose.assert_equal(comp.transitions, self.dfa1.transitions)
        nose.assert_equal(comp.initial_state, self.dfa1.initial_state)
        nose.assert_equal(
            comp.final_states, self.dfa1.states - self.dfa1.final_states)

    def test_union(self):
        """Should compute union of two DFAs."""
        union = self.dfa1 | self.dfa2
        nose.assert_equal(
            union.states,
            {'{q0s0}', '{q0s1}', '{q0s2}', '{q1s0}', '{q1s1}', '{q1s2}'})
        nose.assert_equal(union.symbols, {'a', 'b'})
        nose.assert_equal(union.transitions, {
            '{q0s0}': {'a': '{q0s1}', 'b': '{q1s2}'},
            '{q0s1}': {'a': '{q0s2}', 'b': '{q1s0}'},
            '{q0s2}': {'a': '{q0s0}', 'b': '{q1s1}'},
            '{q1s0}': {'a': '{q1s1}', 'b': '{q0s2}'},
            '{q1s1}': {'a': '{q1s2}', 'b': '{q0s0}'},
            '{q1s2}': {'a': '{q1s0}', 'b': '{q0s1}'}
        })
        nose.assert_equal(union.initial_state, '{q0s0}')
        nose.assert_equal(
            union.final_states,
            {'{q1s0}', '{q1s1}', '{q1s2}', '{q0s2}'})

    def test_union_symbol_mismatch(self):
        """Should raise error if symbol sets are not equal when unioning."""
        self.dfa2.symbols.add('2')
        with nose.assert_raises(automaton.SymbolMismatchError):
            self.dfa1 | self.dfa2

    def test_intersection(self):
        """Should compute intersection of two DFAs."""
        intersection = self.dfa1 & self.dfa2
        nose.assert_equal(
            intersection.states,
            {'{q0s0}', '{q0s1}', '{q0s2}', '{q1s0}', '{q1s1}', '{q1s2}'})
        nose.assert_equal(intersection.symbols, {'a', 'b'})
        nose.assert_equal(intersection.transitions, {
            '{q0s0}': {'a': '{q0s1}', 'b': '{q1s2}'},
            '{q0s1}': {'a': '{q0s2}', 'b': '{q1s0}'},
            '{q0s2}': {'a': '{q0s0}', 'b': '{q1s1}'},
            '{q1s0}': {'a': '{q1s1}', 'b': '{q0s2}'},
            '{q1s1}': {'a': '{q1s2}', 'b': '{q0s0}'},
            '{q1s2}': {'a': '{q1s0}', 'b': '{q0s1}'}
        })
        nose.assert_equal(intersection.initial_state, '{q0s0}')
        nose.assert_equal(intersection.final_states, {'{q1s2}'})
