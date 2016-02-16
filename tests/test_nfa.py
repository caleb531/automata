#!/usr/bin/env python3

import automata.automaton as automaton
import nose.tools as nose
from automata.nfa import NFA


class TestNFA():

    def setup(self):
        # NFA which matches "a", "aaa", or any string where number of 'a's is
        # even and greater than zero
        self.nfa = NFA(**{
            'states': {'q0', 'q1', 'q2', 'q3', 'q4',
                       'q5', 'q6', 'q7', 'q8', 'q9'},
            'symbols': {'a'},
            'transitions': {
                'q0': {'a': {'q1', 'q8'}},
                'q1': {'a': {'q2'}, '': {'q6'}},
                'q2': {'a': {'q3'}},
                'q3': {'': {'q4'}},
                'q4': {'a': {'q5'}},
                'q5': {},
                'q6': {'a': {'q7'}},
                'q7': {},
                'q8': {'a': {'q9'}},
                'q9': {'a': {'q8'}}
            },
            'initial_state': 'q0',
            'final_states': {'q4', 'q6', 'q9'}
        })

    def test_validate_automaton_missing_state(self):
        with nose.assert_raises(automaton.MissingStateError):
            del self.nfa.transitions['q1']
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q10'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.initial_state = 'q10'
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.final_states = {'q10'}
            self.nfa.validate_automaton()

    def test_validate_input_valid_empty_str_done_reading(self):
        nose.assert_equal(self.nfa.validate_input('aaa'), {'q4', 'q7', 'q8'})

    def test_validate_input_valid(self):
        nose.assert_equal(
            self.nfa.validate_input('aaaaaa'), {'q5', 'q7', 'q9'})

    def test_validate_input_valid_empty_str_still_reading(self):
        nose.assert_equal(self.nfa.validate_input('a'), {'q6', 'q8'})

    def test_validate_input_invalid_symbol(self):
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.validate_input('aab')

    def test_validate_input_nonfinal_state(self):
        with nose.assert_raises(automaton.FinalStateError):
            self.nfa.validate_input('aaaaa')
