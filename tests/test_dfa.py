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
            states={'13', '56', '18', '10', '15', '26', '24', '54', '32', '27',
                    '5', '43', '8', '3', '17', '45', '57', '46', '35', '9',
                    '0', '21', '39', '51', '6', '55', '47', '11', '20', '12',
                    '59', '38', '44', '52', '16', '41', '1', '4', '28', '58',
                    '48', '23', '22', '2', '31', '36', '34', '49', '40', '7',
                    '25', '30', '53', '42', '33', '19', '50', '37', '14',
                    '29'},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={'55': {'L': '20', 'U': '49', 'R': '20', 'D': '49'},
                         '57': {'L': '5', 'U': '6', 'R': '1', 'D': '46'},
                         '35': {'L': '44', 'U': '32', 'R': '36', 'D': '33'},
                         '13': {'L': '45', 'U': '23', 'R': '45', 'D': '23'},
                         '43': {'L': '44', 'U': '32', 'R': '44', 'D': '33'},
                         '9': {'L': '5', 'U': '6', 'R': '1', 'D': '6'},
                         '53': {'L': '20', 'U': '33', 'R': '20', 'D': '32'},
                         '12': {'L': '40', 'U': '23', 'R': '25', 'D': '11'},
                         '42': {'L': '1', 'U': '49', 'R': '5', 'D': '49'},
                         '24': {'L': '40', 'U': '48', 'R': '25', 'D': '23'},
                         '27': {'L': '5', 'U': '46', 'R': '1', 'D': '6'},
                         '22': {'L': '40', 'U': '48', 'R': '25', 'D': '11'},
                         '19': {'L': '36', 'U': '32', 'R': '44', 'D': '33'},
                         '59': {'L': '40', 'U': '48', 'R': '45', 'D': '11'},
                         '39': {'L': '45', 'U': '48', 'R': '25', 'D': '11'},
                         '51': {'L': '20', 'U': '18', 'R': '20', 'D': '18'},
                         '34': {'L': '5', 'U': '4', 'R': '1', 'D': '31'},
                         '33': {'L': '44', 'U': '0', 'R': '36', 'D': '28'},
                         '23': {'L': '45', 'U': '8', 'R': '45', 'D': '8'},
                         '46': {'L': '44', 'U': '0', 'R': '44', 'D': '28'},
                         '58': {'L': '5', 'U': '4', 'R': '1', 'D': '4'},
                         '50': {'L': '20', 'U': '28', 'R': '20', 'D': '0'},
                         '54': {'L': '40', 'U': '8', 'R': '25', 'D': '41'},
                         '49': {'L': '1', 'U': '18', 'R': '5', 'D': '18'},
                         '21': {'L': '40', 'U': '26', 'R': '25', 'D': '8'},
                         '16': {'L': '5', 'U': '31', 'R': '1', 'D': '4'},
                         '6': {'L': '40', 'U': '26', 'R': '25', 'D': '41'},
                         '32': {'L': '36', 'U': '0', 'R': '44', 'D': '28'},
                         '48': {'L': '40', 'U': '26', 'R': '45', 'D': '41'},
                         '11': {'L': '45', 'U': '26', 'R': '25', 'D': '41'},
                         '15': {'L': '14', 'U': '49', 'R': '14', 'D': '49'},
                         '1': {'L': '56', 'U': '6', 'R': '37', 'D': '46'},
                         '3': {'L': '4', 'U': '32', 'R': '17', 'D': '33'},
                         '45': {'L': '8', 'U': '23', 'R': '8', 'D': '23'},
                         '52': {'L': '4', 'U': '32', 'R': '4', 'D': '33'},
                         '36': {'L': '56', 'U': '6', 'R': '37', 'D': '6'},
                         '20': {'L': '14', 'U': '33', 'R': '14', 'D': '32'},
                         '25': {'L': '47', 'U': '23', 'R': '10', 'D': '11'},
                         '29': {'L': '37', 'U': '49', 'R': '56', 'D': '49'},
                         '40': {'L': '47', 'U': '48', 'R': '10', 'D': '23'},
                         '5': {'L': '56', 'U': '46', 'R': '37', 'D': '6'},
                         '44': {'L': '47', 'U': '48', 'R': '10', 'D': '11'},
                         '38': {'L': '17', 'U': '32', 'R': '4', 'D': '33'},
                         '2': {'L': '47', 'U': '48', 'R': '8', 'D': '11'},
                         '30': {'L': '8', 'U': '48', 'R': '10', 'D': '11'},
                         '7': {'L': '14', 'U': '18', 'R': '14', 'D': '18'},
                         '37': {'L': '56', 'U': '4', 'R': '37', 'D': '31'},
                         '28': {'L': '4', 'U': '0', 'R': '17', 'D': '28'},
                         '8': {'L': '8', 'U': '8', 'R': '8', 'D': '8'},
                         '31': {'L': '4', 'U': '0', 'R': '4', 'D': '28'},
                         '17': {'L': '56', 'U': '4', 'R': '37', 'D': '4'},
                         '14': {'L': '14', 'U': '28', 'R': '14', 'D': '0'},
                         '10': {'L': '47', 'U': '8', 'R': '10', 'D': '41'},
                         '18': {'L': '37', 'U': '18', 'R': '56', 'D': '18'},
                         '47': {'L': '47', 'U': '26', 'R': '10', 'D': '8'},
                         '56': {'L': '56', 'U': '31', 'R': '37', 'D': '4'},
                         '4': {'L': '47', 'U': '26', 'R': '10', 'D': '41'},
                         '0': {'L': '17', 'U': '0', 'R': '4', 'D': '28'},
                         '26': {'L': '47', 'U': '26', 'R': '8', 'D': '41'},
                         '41': {'L': '8', 'U': '26', 'R': '10', 'D': '41'}},
            initial_state='55',
            final_states={'15', '24', '54', '32', '27', '5', '43', '57', '3',
                          '46', '35', '9', '21', '39', '51', '6', '55', '11',
                          '20', '12', '59', '38', '44', '52', '16', '1', '58',
                          '48', '22', '2', '36', '34', '49', '40', '25', '30',
                          '53', '42', '33', '19', '50', '29'})
        check_dfa = DFA(
            states={'5', '36', '1', '49', '40', '25', '46', '6', '55',
                    '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}', '33',
                    '11', '20', '48', '44', '32'},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={
                '48':
                {'L': '40',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '44':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '48',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '11'},
                '40':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '48',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '33':
                {'L': '44',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '36',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '55': {'L': '20', 'U': '49', 'R': '20', 'D': '49'},
                '32':
                {'L': '36',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '44',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '46':
                {'L': '44',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '44',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '25':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '11'},
                '6':
                {'L': '40',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '25',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '11':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '25',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '5':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '46',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '6'},
                '49':
                {'L': '1',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '5',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '20':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '33',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '32'},
                '36':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '6',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '6'},
                '1':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '6',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '46'}},
            initial_state='55',
            final_states={'5', '1', '36', '49', '40', '25', '46', '6', '55',
                          '33', '11', '20', '48', '44', '32'})
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, check_dfa.states)
        nose.assert_equal(minimal_dfa.input_symbols, check_dfa.input_symbols)
        nose.assert_equal(minimal_dfa.transitions, check_dfa.transitions)
        nose.assert_equal(minimal_dfa.initial_state, check_dfa.initial_state)
        nose.assert_equal(minimal_dfa.final_states, check_dfa.final_states)

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

    def test_dfa_show_diagram(self):
        """ testing show_diagram method in DFA class """
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        graph = dfa.show_diagram("dfa_graph", horizontal=True,
                                 reverse_orientation=False, cleanup=False)
        nose.assert_true(graph)
        graph = dfa.show_diagram(horizontal=True, reverse_orientation=True)
        nose.assert_true(graph)
        graph = dfa.show_diagram(horizontal=False, reverse_orientation=True)
        nose.assert_true(graph)
        graph = dfa.show_diagram(horizontal=False, reverse_orientation=False)
        nose.assert_true(graph)
