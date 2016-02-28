#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""

import nose.tools as nose

import automata.automaton as automaton
from automata.dfa import DFA
from automata.nfa import NFA


class TestNFA(object):
    """A test class for testing nondeterministic finite automata."""

    def setup(self):
        """Reset test NFA before every test function."""
        # NFA which matches strings beginning with 'a', ending with 'a', and
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

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = NFA(self.nfa)
        nose.assert_is_not(new_nfa.states, self.nfa.states)
        nose.assert_equal(new_nfa.states, self.nfa.states)
        nose.assert_is_not(new_nfa.symbols, self.nfa.symbols)
        nose.assert_equal(new_nfa.symbols, self.nfa.symbols)
        nose.assert_is_not(new_nfa.transitions, self.nfa.transitions)
        for start_state, paths in new_nfa.transitions.items():
            nose.assert_is_not(paths, self.nfa.transitions[start_state])
            for symbol, end_states in paths.items():
                nose.assert_is_not(
                    end_states,
                    self.nfa.transitions[start_state][symbol])
                nose.assert_equal(
                    end_states,
                    self.nfa.transitions[start_state][symbol])
        nose.assert_equal(new_nfa.initial_state, self.nfa.initial_state)
        nose.assert_is_not(new_nfa.final_states, self.nfa.final_states)
        nose.assert_equal(new_nfa.final_states, self.nfa.final_states)

    def test_init_dfa(self):
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA(DFA(
            states={'q0', 'q1', 'q2'},
            symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        ))
        nose.assert_equal(nfa.states, {'q0', 'q1', 'q2'})
        nose.assert_equal(nfa.symbols, {'0', '1'})
        nose.assert_equal(nfa.transitions, {
            'q0': {'0': {'q0'}, '1': {'q1'}},
            'q1': {'0': {'q0'}, '1': {'q2'}},
            'q2': {'0': {'q2'}, '1': {'q1'}}
        })
        nose.assert_equal(nfa.initial_state, 'q0')

    def test_validate_automaton_missing_state(self):
        """Should raise error if a state has no transitions defined."""
        with nose.assert_raises(automaton.MissingStateError):
            del self.nfa.transitions['q1']
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q3'}
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.initial_state = 'q3'
            self.nfa.validate_automaton()

    def test_validate_automaton_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(automaton.InvalidStateError):
            self.nfa.final_states = {'q3'}
            self.nfa.validate_automaton()

    def test_validate_input_valid(self):
        """Should return correct stop states if valid NFA input is given."""
        nose.assert_equal(self.nfa.validate_input('aba'), {'q1', 'q2'})

    def test_validate_input_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(automaton.InvalidSymbolError):
            self.nfa.validate_input('abc')

    def test_validate_input_nonfinal_state(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(automaton.FinalStateError):
            self.nfa.validate_input('abba')

    def test_cyclic_lambda_transitions(self):
        """Should traverse NFA containing cyclic lambda transitions."""
        # NFA which matches zero or more occurrences of 'a'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            symbols={'a'},
            transitions={
                'q0': {'': {'q1', 'q3'}},
                'q1': {'a': {'q2'}},
                'q2': {'': {'q3'}},
                'q3': {'': {'q0'}}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_equal(nfa.validate_input(''), {'q0', 'q1', 'q3'})
        nose.assert_equal(nfa.validate_input('a'), {'q0', 'q1', 'q2', 'q3'})
