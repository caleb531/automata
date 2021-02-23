#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestDFA(test_fa.TestFA):
    """A test class for testing deterministic finite automata."""

    def test_init_dfa(self):
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = DFA.copy(self.dfa)
        self.assert_is_copy(new_dfa, self.dfa)

    def test_init_dfa_missing_formal_params(self):
        """Should raise an error if formal DFA parameters are missing."""
        with nose.assert_raises(TypeError):
            DFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_dfa(self):
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assert_is_copy(new_dfa, self.dfa)

    @patch('automata.fa.dfa.DFA.validate')
    def test_init_validation(self, validate):
        """Should validate DFA when initialized."""
        DFA.copy(self.dfa)
        validate.assert_called_once_with()

    def test_dfa_equal(self):
        """Should correctly determine if two DFAs are equal."""
        new_dfa = self.dfa.copy()
        nose.assert_true(self.dfa == new_dfa, 'DFAs are not equal')

    def test_dfa_not_equal(self):
        """Should correctly determine if two DFAs are not equal."""
        new_dfa = self.dfa.copy()
        new_dfa.final_states.add('q2')
        nose.assert_true(self.dfa != new_dfa, 'DFAs are equal')

    def test_validate_missing_state(self):
        """Should raise error if a state has no transitions defined."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.dfa.transitions['q1']
            self.dfa.validate()

    def test_validate_missing_symbol(self):
        """Should raise error if a symbol transition is missing."""
        with nose.assert_raises(exceptions.MissingSymbolError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate()

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate()

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.final_states = {3}
            self.dfa.validate()

    def test_read_input_accepted(self):
        """Should return correct state if acceptable DFA input is given."""
        nose.assert_equal(self.dfa.read_input('0111'), 'q1')

    def test_read_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dfa.read_input('011')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dfa.read_input('01112')

    def test_accepts_input_true(self):
        """Should return True if DFA input is accepted."""
        nose.assert_equal(self.dfa.accepts_input('0111'), True)

    def test_accepts_input_false(self):
        """Should return False if DFA input is rejected."""
        nose.assert_equal(self.dfa.accepts_input('011'), False)

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dfa.read_input_stepwise('0111')
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        nose.assert_equal(list(validation_generator), [
            'q0', 'q0', 'q1', 'q2', 'q1'
        ])

    def test_minify_dfa(self):
        """Should minify a given DFA."""
        # This DFA accepts all words which are at least two characters long.
        # The states q1/q2 and q3/q4/q5/q6 are redundant.
        # The state q7 is not reachable.
        dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q2'},
                'q1': {'0': 'q3', '1': 'q4'},
                'q2': {'0': 'q5', '1': 'q6'},
                'q3': {'0': 'q3', '1': 'q3'},
                'q4': {'0': 'q4', '1': 'q4'},
                'q5': {'0': 'q5', '1': 'q5'},
                'q6': {'0': 'q6', '1': 'q6'},
                'q7': {'0': 'q7', '1': 'q7'}
            },
            initial_state='q0',
            final_states={'q3', 'q4', 'q5', 'q6'}
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {
            'q0', '{q1,q2}', '{q3,q4,q5,q6}'
        })
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            'q0': {'0': '{q1,q2}', '1': '{q1,q2}'},
            '{q1,q2}': {'0': '{q3,q4,q5,q6}', '1': '{q3,q4,q5,q6}'},
            '{q3,q4,q5,q6}': {'0': '{q3,q4,q5,q6}', '1': '{q3,q4,q5,q6}'}
        })
        nose.assert_equal(minimal_dfa.initial_state, 'q0')
        nose.assert_equal(minimal_dfa.final_states, {'{q3,q4,q5,q6}'})

    def test_minify_dfa_complex(self):
        dfa = DFA(
            states={'{1,3}', '{3,2}', '{1,0}', '{0,2}', '{3,1}', '{2,1}',
                    '{2,2}', '{1,2}', '{0,1}', '{2,0}', '{0,0}', '{0,3}',
                    '{3,0}', '{1,1}', '{3,3}', '{2,3}'},
            input_symbols={'D', 'L', 'R', 'U'},
            transitions={
                '{0,0}':
                {'D': '{1,0}', 'L': '{2,3}', 'R': '{2,3}',
                 'U': '{1,0}'},
                '{0,1}':
                {'D': '{1,0}', 'L': '{2,2}', 'R': '{2,2}',
                 'U': '{1,0}'},
                '{0,2}':
                {'D': '{1,3}', 'L': '{2,2}', 'R': '{2,2}',
                 'U': '{1,3}'},
                '{0,3}':
                {'D': '{1,3}', 'L': '{2,3}', 'R': '{2,3}',
                 'U': '{1,3}'},
                '{1,0}':
                {'D': '{3,0}', 'L': '{2,3}', 'R': '{2,3}',
                 'U': '{3,0}'},
                '{1,1}':
                {'D': '{3,0}', 'L': '{2,2}', 'R': '{2,2}',
                 'U': '{3,0}'},
                '{1,2}':
                {'D': '{3,3}', 'L': '{2,2}', 'R': '{2,2}',
                 'U': '{3,3}'},
                '{1,3}':
                {'D': '{3,3}', 'L': '{2,3}', 'R': '{2,3}',
                 'U': '{3,3}'},
                '{2,0}':
                {'D': '{1,0}', 'L': '{3,3}', 'R': '{3,3}',
                 'U': '{1,0}'},
                '{2,1}':
                {'D': '{1,0}', 'L': '{3,2}', 'R': '{3,2}',
                 'U': '{1,0}'},
                '{2,2}':
                {'D': '{1,3}', 'L': '{3,2}', 'R': '{3,2}',
                 'U': '{1,3}'},
                '{2,3}':
                {'D': '{1,3}', 'L': '{3,3}', 'R': '{3,3}',
                 'U': '{1,3}'},
                '{3,0}':
                {'D': '{3,0}', 'L': '{3,3}', 'R': '{3,3}',
                 'U': '{3,0}'},
                '{3,1}':
                {'D': '{3,0}', 'L': '{3,2}', 'R': '{3,2}',
                 'U': '{3,0}'},
                '{3,2}':
                {'D': '{3,3}', 'L': '{3,2}', 'R': '{3,2}',
                 'U': '{3,3}'},
                '{3,3}':
                {'D': '{3,3}', 'L': '{3,3}', 'R': '{3,3}',
                 'U': '{3,3}'}},
            initial_state='{0,1}',
            final_states={'{2,1}', '{2,2}', '{0,1}', '{1,2}', '{2,0}',
                          '{0,0}', '{1,1}', '{1,0}', '{0,2}'})
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {
            '{{1,3},{2,3},{3,0},{3,2},{3,3}}', '{{1,0},{2,2}}', '{0,1}'
        })
        nose.assert_equal(minimal_dfa.input_symbols, {'D', 'L', 'R', 'U'})
        nose.assert_equal(minimal_dfa.transitions, {
            '{{1,0},{2,2}}': {
                'D': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'L': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'R': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'U': '{{1,3},{2,3},{3,0},{3,2},{3,3}}'
            },
            '{0,1}': {
                'D': '{{1,0},{2,2}}',
                'L': '{{1,0},{2,2}}',
                'R': '{{1,0},{2,2}}',
                'U': '{{1,0},{2,2}}'
            },
            '{{1,3},{2,3},{3,0},{3,2},{3,3}}': {
                'D': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'L': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'R': '{{1,3},{2,3},{3,0},{3,2},{3,3}}',
                'U': '{{1,3},{2,3},{3,0},{3,2},{3,3}}'
            }
        })
        nose.assert_equal(minimal_dfa.initial_state, '{0,1}')
        nose.assert_equal(minimal_dfa.final_states, {'{{1,0},{2,2}}', '{0,1}'})

    def test_minify_minimal_dfa(self):
        """Should minify an already minimal DFA."""
        # This DFA just accepts words ending in 1.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, dfa.states)
        nose.assert_equal(minimal_dfa.input_symbols, dfa.input_symbols)
        nose.assert_equal(minimal_dfa.transitions, dfa.transitions)
        nose.assert_equal(minimal_dfa.initial_state, dfa.initial_state)
        nose.assert_equal(minimal_dfa.final_states, dfa.final_states)

    def test_minify_dfa_initial_state(self):
        """Should minify a DFA where the initial state is being changed."""
        # This DFA accepts all words with ones and zeroes.
        # The two states can be merged into one.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states={'q0', 'q1'},
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {'{q0,q1}'})
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            '{q0,q1}': {'0': '{q0,q1}', '1': '{q0,q1}'},
        })
        nose.assert_equal(minimal_dfa.initial_state, '{q0,q1}')
        nose.assert_equal(minimal_dfa.final_states, {'{q0,q1}'})

    def test_minify_dfa_no_final_states(self):
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states=set(),
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {'{q0,q1}'})
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            '{q0,q1}': {'0': '{q0,q1}', '1': '{q0,q1}'},
        })
        nose.assert_equal(minimal_dfa.initial_state, '{q0,q1}')
        nose.assert_equal(minimal_dfa.final_states, set())

    def test_init_nfa_simple(self):
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}},
                'q1': {'1': {'q2'}},
                'q2': {}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA.from_nfa(nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q0,q1}', '{q2}'})
        nose.assert_equal(dfa.input_symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'0': '{}', '1': '{}'},
            '{q0}': {'0': '{q0,q1}', '1': '{}'},
            '{q0,q1}': {'0': '{q0,q1}', '1': '{q2}'},
            '{q2}': {'0': '{}', '1': '{}'}
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q2}'})

    def test_init_nfa_more_complex(self):
        """Should convert to a DFA a more complex NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}, '1': {'q0'}},
                'q1': {'0': {'q1'}, '1': {'q2'}},
                'q2': {'0': {'q2'}, '1': {'q1'}}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA.from_nfa(nfa)
        nose.assert_equal(dfa.states, {
            '{q0}', '{q0,q1}', '{q0,q2}', '{q0,q1,q2}'
        })
        nose.assert_equal(dfa.input_symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            '{q0}': {'1': '{q0}', '0': '{q0,q1}'},
            '{q0,q1}': {'1': '{q0,q2}', '0': '{q0,q1}'},
            '{q0,q2}': {'1': '{q0,q1}', '0': '{q0,q1,q2}'},
            '{q0,q1,q2}': {'1': '{q0,q1,q2}', '0': '{q0,q1,q2}'}
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q0,q1,q2}', '{q0,q2}'})

    def test_init_nfa_lambda_transition(self):
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA.from_nfa(self.nfa)
        nose.assert_equal(dfa.states, {'{}', '{q0}', '{q1,q2}'})
        nose.assert_equal(dfa.input_symbols, {'a', 'b'})
        nose.assert_equal(dfa.transitions, {
            '{}': {'a': '{}', 'b': '{}'},
            '{q0}': {'a': '{q1,q2}', 'b': '{}'},
            '{q1,q2}': {'a': '{q1,q2}', 'b': '{q0}'},
        })
        nose.assert_equal(dfa.initial_state, '{q0}')
        nose.assert_equal(dfa.final_states, {'{q1,q2}'})

    def test_nfa_to_dfa_with_lambda_transitions(self):
        """ Test NFA->DFA when initial state has lambda transitions """
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'': {'q2'}},
                'q1': {'a': {'q1'}},
                'q2': {'a': {'q1'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        dfa = DFA.from_nfa(nfa)  # returns an equivalent DFA
        nose.assert_equal(dfa.read_input('a'), '{q1}')
