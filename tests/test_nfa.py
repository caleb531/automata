#!/usr/bin/env python3

import json
import automata.automaton as automaton
import nose.tools as nose
from automata.nfa import NFA


class TestNFA():

    def setup(self):
        # NFA which matches strings beginning with "a", ending with "a", and
        # containing no consecutive 'b's
        self.nfa = NFA(
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

    def test_init_json(self):
        """should copy given JSON object into new NFA"""
        with open('tests/files/nfa.json', 'r') as nfa_file:
            nfa_json = json.load(nfa_file)
        new_nfa = NFA(**nfa_json)
        nose.assert_equal(new_nfa.states, set(nfa_json['states']))
        nose.assert_is_not(new_nfa.states, nfa_json['states'])
        nose.assert_equal(new_nfa.symbols, set(nfa_json['symbols']))
        nose.assert_is_not(new_nfa.symbols, nfa_json['symbols'])
        nose.assert_is_not(new_nfa.transitions, nfa_json['transitions'])
        for start_state, paths in new_nfa.transitions.items():
            nose.assert_is_not(paths, nfa_json['transitions'][start_state])
            for symbol, end_states in paths.items():
                nose.assert_equal(
                    end_states,
                    set(nfa_json['transitions'][start_state][symbol]))
        nose.assert_equal(new_nfa.initial_state, nfa_json['initial_state'])
        nose.assert_equal(new_nfa.final_states, set(nfa_json['final_states']))
        nose.assert_is_not(new_nfa.final_states, nfa_json['final_states'])

    def test_validate_automaton_missing_state(self):
        """should raise error if a state has no transitions defined"""
        with nose.assert_raises(automaton.MissingStateError):
            del self.nfa.transitions['q1']
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        """should raise error if a transition references an invalid symbol"""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        """should raise error if a transition references an invalid state"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q3'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        """should raise error if the initial state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.initial_state = 'q3'
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        """should raise error if the final state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.final_states = {'q3'}
            self.nfa.validate_automaton()

    def test_validate_input_valid(self):
        """should return correct stop states when valid NFA input is given"""
        nose.assert_equal(self.nfa.validate_input('aba'), {'q1', 'q2'})

    def test_validate_input_invalid_symbol(self):
        """should raise error if an invalid symbol is read"""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.validate_input('abc')

    def test_validate_input_nonfinal_state(self):
        """should raise error if the stop state is not a final state"""
        with nose.assert_raises(automaton.FinalStateError):
            self.nfa.validate_input('abba')
