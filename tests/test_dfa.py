#!/usr/bin/env python3

import automata.automaton as automaton
import nose.tools as nose
from automata.dfa import DFA
from automata.nfa import NFA


class TestDFA(object):

    def setup(self):
        # DFA which matches all binary strings ending in an odd number of '1's
        self.dfa = DFA(
            states={'q0', 'q1', 'q2'},
            symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )

    def test_init_dfa(self):
        """should copy DFA if passed into DFA constructor"""
        new_dfa = DFA(self.dfa)
        nose.assert_is_not(new_dfa.states, self.dfa.states)
        nose.assert_equal(new_dfa.states, self.dfa.states)
        nose.assert_is_not(new_dfa.symbols, self.dfa.symbols)
        nose.assert_equal(new_dfa.symbols, self.dfa.symbols)
        nose.assert_is_not(new_dfa.transitions, self.dfa.transitions)
        nose.assert_equal(new_dfa.transitions, self.dfa.transitions)
        nose.assert_equal(new_dfa.initial_state, self.dfa.initial_state)
        nose.assert_is_not(new_dfa.final_states, self.dfa.final_states)
        nose.assert_equal(new_dfa.final_states, self.dfa.final_states)

    def test_validate_automaton_missing_state(self):
        """should raise error if a state has no transitions defined"""
        with nose.assert_raises(automaton.MissingStateError):
            del self.dfa.transitions['q1']
            self.dfa.validate_automaton()

    def test_validate_automaton_missing_symbol(self):
        """should raise error if a symbol transition is missing"""
        with nose.assert_raises(automaton.MissingSymbolError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        """should raise error if a transition references an invalid symbol"""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        """should raise error if a transition references an invalid state"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        """should raise error if the initial state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        """should raise error if the final state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate_automaton()

    def test_validate_input_valid(self):
        """should return correct stop state when valid DFA input is given"""
        nose.assert_equal(self.dfa.validate_input('0111'), 'q1')

    def test_validate_input_invalid_symbol(self):
        """should raise error if an invalid symbol is read"""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.validate_input('01112')

    def test_validate_input_nonfinal_state(self):
        """should raise error if the stop state is not a final state"""
        with nose.assert_raises(automaton.FinalStateError):
            self.dfa.validate_input('011')

    def test_init_nfa_simple(self):
        """should properly convert a simple NFA to a DFA"""
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
        """should properly convert an NFA with a lambda transition to a DFA"""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}},
                'q1': {'a': {'q1'}, '': {'q2'}},
                'q2': {'b': {'q0'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        dfa = DFA(nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q1q2}'})
        nose.assert_equal(dfa.symbols, {'a', 'b'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'a': '{}', 'b': '{}'},
            '{q0}': {'a': '{q1q2}', 'b': '{}'},
            '{q1q2}': {'a': '{q1q2}', 'b': '{q0}'},
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q1q2}'})
