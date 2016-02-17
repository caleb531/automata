#!/usr/bin/env python3

import json
import automata.automaton as automaton
import nose.tools as nose
from automata.dfa import DFA


class TestDFA():

    def setup(self):
        # DFA which matches all binary strings ending in an odd number of '1's
        self.dfa = DFA(**{
            'states': {'q0', 'q1', 'q2'},
            'symbols': {'0', '1'},
            'transitions': {
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q1'}
            },
            'initial_state': 'q0',
            'final_states': {'q1'}
        })

    def test_init_json(self):
        """should copy given JSON object into new DFA"""
        with open('tests/files/dfa.JSON', 'r') as dfa_file:
            dfa_json = json.load(dfa_file)
        new_dfa = DFA(**dfa_json)
        nose.assert_equal(new_dfa.states, set(dfa_json['states']))
        nose.assert_is_not(new_dfa.states, dfa_json['states'])
        nose.assert_equal(new_dfa.symbols, set(dfa_json['symbols']))
        nose.assert_is_not(new_dfa.symbols, dfa_json['symbols'])
        nose.assert_equal(new_dfa.transitions, dict(dfa_json['transitions']))
        nose.assert_is_not(new_dfa.transitions, dfa_json['transitions'])
        nose.assert_equal(new_dfa.final_states, set(dfa_json['final_states']))
        nose.assert_is_not(new_dfa.final_states, dfa_json['final_states'])

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
