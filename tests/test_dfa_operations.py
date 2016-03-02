#!/usr/bin/env python3
"""Classes and functions for testing DFA operations."""

import nose.tools as nose

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
        # Attributes of the union of dfa1 and dfa2, available for convenience
        self.union_states = {
            '{q0s0}', '{q0s1}', '{q0s2}', '{q1s0}', '{q1s1}', '{q1s2}'}
        self.union_symbols = {'a', 'b'}
        self.union_transitions = {
            '{q0s0}': {'a': '{q0s1}', 'b': '{q1s2}'},
            '{q0s1}': {'a': '{q0s2}', 'b': '{q1s0}'},
            '{q0s2}': {'a': '{q0s0}', 'b': '{q1s1}'},
            '{q1s0}': {'a': '{q1s1}', 'b': '{q0s2}'},
            '{q1s1}': {'a': '{q1s2}', 'b': '{q0s0}'},
            '{q1s2}': {'a': '{q1s0}', 'b': '{q0s1}'}
        }
        self.union_initial_state = '{q0s0}'

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
        nose.assert_equal(union.states, self.union_states)
        nose.assert_equal(union.symbols, self.union_symbols)
        nose.assert_equal(union.transitions, self.union_transitions)
        nose.assert_equal(union.initial_state, self.union_initial_state)
        nose.assert_equal(
            union.final_states,
            {'{q1s0}', '{q1s1}', '{q1s2}', '{q0s2}'})

    def test_union_different_symbol_sets(self):
        """Should union symbol sets of operands when unioning."""
        dfa3 = DFA(
            states={'q0'},
            symbols={'a'},
            transitions={'q0': {'a': 'q0'}},
            initial_state='q0',
            final_states={'q0'}
        )
        nose.assert_equal(dfa3.validate_input(''), 'q0')
        nose.assert_equal(dfa3.validate_input('aaa'), 'q0')
        dfa4 = DFA(
            states={'s0', 's1'},
            symbols={'b'},
            transitions={'s0': {'b': 's1'}, 's1': {'b': 's1'}},
            initial_state='s0',
            final_states={'s1'}
        )
        union = dfa3 | dfa4
        nose.assert_equal(
            union.states,
            {'{q0s0}', '{q0s1}', '{q0{}}', '{{}s0}', '{{}s1}', '{{}{}}'})
        nose.assert_equal(union.symbols, {'a', 'b'})
        nose.assert_equal(
            union.final_states, {'{q0s0}', '{q0s1}', '{q0{}}', '{{}s1}'})

    def test_intersection(self):
        """Should compute intersection of two DFAs."""
        inter = self.dfa1 & self.dfa2
        nose.assert_equal(inter.states, self.union_states)
        nose.assert_equal(inter.symbols, self.union_symbols)
        nose.assert_equal(inter.transitions, self.union_transitions)
        nose.assert_equal(inter.initial_state, self.union_initial_state)
        nose.assert_equal(inter.final_states, {'{q1s2}'})

    def test_difference(self):
        """Should compute difference of two DFAs."""
        diff = self.dfa1 - self.dfa2
        nose.assert_equal(diff.states, self.union_states)
        nose.assert_equal(diff.symbols, self.union_symbols)
        nose.assert_equal(diff.transitions, self.union_transitions)
        nose.assert_equal(diff.initial_state, self.union_initial_state)
        nose.assert_equal(diff.final_states, {'{q1s0}', '{q1s1}'})
