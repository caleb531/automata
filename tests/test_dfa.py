#!/usr/bin/env python3

import automata.automaton as automaton
import nose.tools as nose
from automata.dfa import DFA


class TestDFA():

    def setup(self):
        # DFA which matches all binary strings ending in an odd number of 1s
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

    def test_validate_automaton_missing_state(self):
        with nose.assert_raises(automaton.MissingStateError):
            del self.dfa.transitions['q1']
            self.dfa.validate_automaton()

    def test_validate_automaton_missing_symbol(self):
        with nose.assert_raises(automaton.MissingSymbolError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate_automaton()

    def test_validate_input_valid(self):
        nose.assert_equal(self.dfa.validate_input('0111'), True)

    def test_validate_input_invalid_symbol(self):
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.dfa.validate_input('01112')

    def test_validate_input_nonfinal_state(self):
        with nose.assert_raises(automaton.FinalStateError):
            self.dfa.validate_input('011')
