#!/usr/bin/env python3

import automata.automaton as automaton
import nose.tools as nose
from automata.nfa import NFA


class TestNFA():

    def setup(self):
        # NFA which matches "a", "aaa", or any string of 'a's where number of
        # 'a's is even and greater than zero
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
            self.nfa.transitions['q1']['a'] = {'q10'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        """should raise error if the initial state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.initial_state = 'q10'
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        """should raise error if the final state is invalid"""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.final_states = {'q10'}
            self.nfa.validate_automaton()

    def test_validate_input_valid(self):
        """should return correct stop states when valid DFA input is given"""
        nose.assert_equal(
            self.nfa.validate_input('aaaaaa'), {'q5', 'q7', 'q9'})

    def test_validate_input_empty_str(self):
        """should resolve any empty state transitions on the stop states"""
        nose.assert_equal(self.nfa.validate_input('aaa'), {'q4', 'q7', 'q8'})

    def test_validate_input_invalid_symbol(self):
        """should raise error if an invalid symbol is read"""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.validate_input('aab')

    def test_validate_input_nonfinal_state(self):
        """should raise error if the stop state is not a final state"""
        with nose.assert_raises(automaton.FinalStateError):
            self.nfa.validate_input('aaaaa')

    def test_from_file(self):
        """should construct a new NFA from the given file path's contents"""
        nose.assert_equal(
            NFA.from_file('./tests/files/nfa.json').__dict__,
            self.nfa.__dict__)
