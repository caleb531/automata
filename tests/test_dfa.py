#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import nose.tools as nose

import automata.automaton as automaton
import tests.test_automaton as test_automaton
from automata.dfa import DFA
from automata.nfa import NFA


class TestDFA(test_automaton.TestAutomaton):
    """A test class for testing deterministic finite automata."""

    def test_init_dfa(self):
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = DFA(self.dfa)
        self.assert_is_copy(new_dfa, self.dfa)

    def test_copy_dfa(self):
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assert_is_copy(new_dfa, self.dfa)

    def test_validate_automaton_missing_state(self):
        """Should raise error if a state has no transitions defined."""
        with nose.assert_raises(automaton.MissingStateError):
            del self.dfa.transitions['q1']
            self.dfa.validate_automaton()

    def test_validate_automaton_missing_symbol(self):
        """Should raise error if a symbol transition is missing."""
        with nose.assert_raises(automaton.MissingSymbolError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate_automaton()

    def test_validate_input_valid(self):
        """Should return correct stop state if valid DFA input is given."""
        nose.assert_equal(self.dfa.validate_input('0111'), 'q1')

    def test_validate_input_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.validate_input('01112')

    def test_validate_input_nonfinal_state(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(automaton.FinalStateError):
            self.dfa.validate_input('011')

    def test_init_nfa_simple(self):
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}},
                'q1': {'1': {'q2'}},
                'q2': {}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA(nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q0q1}', '{q2}'})
        nose.assert_equal(dfa.symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'0': '{}', '1': '{}'},
            '{q0}': {'0': '{q0q1}', '1': '{}'},
            '{q0q1}': {'0': '{q0q1}', '1': '{q2}'},
            '{q2}': {'0': '{}', '1': '{}'}
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q2}'})

    def test_init_nfa_lambda_transition(self):
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA(self.nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q1q2}'})
        nose.assert_equal(dfa.symbols, {'a', 'b'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'a': '{}', 'b': '{}'},
            '{q0}': {'a': '{q1q2}', 'b': '{}'},
            '{q1q2}': {'a': '{q1q2}', 'b': '{q0}'},
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q1q2}'})
