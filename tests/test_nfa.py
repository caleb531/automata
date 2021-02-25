#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = NFA.copy(self.nfa)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with nose.assert_raises(TypeError):
            NFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_nfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_dfa(self):
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA.from_dfa(self.dfa)
        nose.assert_equal(nfa.states, {'q0', 'q1', 'q2'})
        nose.assert_equal(nfa.input_symbols, {'0', '1'})
        nose.assert_equal(nfa.transitions, {
            'q0': {'0': {'q0'}, '1': {'q1'}},
            'q1': {'0': {'q0'}, '1': {'q2'}},
            'q2': {'0': {'q2'}, '1': {'q1'}}
        })
        nose.assert_equal(nfa.initial_state, 'q0')

    @patch('automata.fa.nfa.NFA.validate')
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        NFA.copy(self.nfa)
        validate.assert_called_once_with()

    def test_nfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_nfa = self.nfa.copy()
        nose.assert_true(self.nfa == new_nfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_nfa = self.nfa.copy()
        new_nfa.final_states.add('q2')
        nose.assert_true(self.nfa != new_nfa, 'NFAs are equal')

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.nfa.transitions['q1']['c'] = {'q2'}
            self.nfa.validate()

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.nfa.transitions['q1']['a'] = {'q3'}
            self.nfa.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.nfa.initial_state = 'q3'
            self.nfa.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.nfa.transitions[self.nfa.initial_state]
            self.nfa.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.nfa.final_states = {'q3'}
            self.nfa.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.nfa.final_states = {3}
            self.nfa.validate()

    def test_read_input_accepted(self):
        """Should return correct states if acceptable NFA input is given."""
        nose.assert_equal(self.nfa.read_input('aba'), {'q1', 'q2'})

    def test_validate_missing_state(self):
        """Should silently ignore states without transitions defined."""
        self.nfa.states.add('q3')
        self.nfa.transitions['q0']['a'].add('q3')
        nose.assert_equal(self.nfa.validate(), True)

    def test_read_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.nfa.read_input('abba')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.nfa.read_input('abc')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise('aba')
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        nose.assert_equal(list(validation_generator), [
            {'q0'}, {'q1', 'q2'}, {'q0'}, {'q1', 'q2'}
        ])

    def test_accepts_input_true(self):
        """Should return True if NFA input is accepted."""
        nose.assert_equal(self.nfa.accepts_input('aba'), True)

    def test_accepts_input_false(self):
        """Should return False if NFA input is rejected."""
        nose.assert_equal(self.nfa.accepts_input('abba'), False)

    def test_cyclic_lambda_transitions(self):
        """Should traverse NFA containing cyclic lambda transitions."""
        # NFA which matches zero or more occurrences of 'a'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a'},
            transitions={
                'q0': {'': {'q1', 'q3'}},
                'q1': {'a': {'q2'}},
                'q2': {'': {'q3'}},
                'q3': {'': {'q0'}}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_equal(nfa.read_input(''), {'q0', 'q1', 'q3'})
        nose.assert_equal(nfa.read_input('a'), {'q0', 'q1', 'q2', 'q3'})

    def test_non_str_states(self):
        """should handle non-string state names"""
        nfa = NFA(
            states={0},
            input_symbols={0},
            transitions={0: {}},
            initial_state=0,
            final_states=set())
        # We don't care what the output is, just as long as no exception is
        # raised
        nose.assert_not_equal(nfa.accepts_input(''), None)

    def test_nfa_show_diagram(self):
        """ testing show_diagram method in NFA class """
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}},
                'q1': {'a': {'q1'}, '': {'q2'}},
                'q2': {'b': {'q0'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        graph = nfa.show_diagram("nfa_graph", horizontal=True,
                                 reverse_orientation=False, cleanup=False)
        nose.assert_true(graph)
        graph = nfa.show_diagram(horizontal=True, reverse_orientation=True)
        nose.assert_true(graph)
        graph = nfa.show_diagram(horizontal=False, reverse_orientation=True)
        nose.assert_true(graph)
        graph = nfa.show_diagram(horizontal=False, reverse_orientation=False)
        nose.assert_true(graph)
