#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import types
from unittest.mock import patch

import unittest

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.dtm import DTM


class TestDTM(test_tm.TestTM):
    """A test class for testing deterministic Turing machines."""

    def test_init_dtm(self):
        """Should copy DTM if passed into DTM constructor."""
        new_dtm = DTM.copy(self.dtm1)
        self.assert_is_copy(new_dtm, self.dtm1)

    def test_init_dtm_missing_formal_params(self):
        """Should raise an error if formal DTM parameters are missing."""
        with self.assertRaises(TypeError):
            DTM(
                states={'q0', 'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                tape_symbols={'0', '1', 'x', 'y', '.'},
                initial_state='q0',
                blank_symbol='.',
                final_states={'q4'}
            )

    @patch('automata.tm.dtm.DTM.validate')
    def test_init_validation(self, validate):
        """Should validate DTM when initialized."""
        DTM.copy(self.dtm1)
        validate.assert_called_once_with()

    def test_copy_dtm(self):
        """Should create exact copy of DTM if copy() method is called."""
        new_dtm = self.dtm1.copy()
        self.assert_is_copy(new_dtm, self.dtm1)

    def test_dtm_equal(self):
        """Should correctly determine if two DTMs are equal."""
        new_dtm = self.dtm1.copy()
        self.assertTrue(self.dtm1 == new_dtm, 'DTMs are not equal')

    def test_dtm_not_equal(self):
        """Should correctly determine if two DTMs are not equal."""
        new_dtm = self.dtm1.copy()
        new_dtm.final_states.add('q2')
        self.assertTrue(self.dtm1 != new_dtm, 'DTMs are equal')

    def test_validate_input_symbol_subset(self):
        """Should raise error if any input symbols are not tape symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            self.dtm1.input_symbols.add('2')
            self.dtm1.validate()

    def test_validate_invalid_transition_state(self):
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dtm1.transitions['q5'] = self.dtm1.transitions['q0']
            self.dtm1.validate()

    def test_validate_invalid_transition_symbol(self):
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dtm1.transitions['q0']['2'] = ('q0', '0' 'R')
            self.dtm1.validate()

    def test_validate_invalid_transition_result_state(self):
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dtm1.transitions['q0']['y'] = ('q5', 'y', 'R')
            self.dtm1.validate()

    def test_validate_invalid_transition_result_symbol(self):
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dtm1.transitions['q0']['y'] = ('q3', 'z', 'R')
            self.dtm1.validate()

    def test_validate_invalid_transition_result_direction(self):
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            self.dtm1.transitions['q0']['y'] = ('q3', 'y', 'U')
            self.dtm1.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dtm1.initial_state = 'q5'
            self.dtm1.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            del self.dtm1.transitions[self.dtm1.initial_state]
            self.dtm1.validate()

    def test_validate_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            self.dtm1.final_states.add('q0')
            self.dtm1.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dtm1.final_states = {'q5'}
            self.dtm1.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dtm1.final_states = {5}
            self.dtm1.validate()

    def test_validate_final_state_transitions(self):
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            self.dtm1.transitions['q4'] = {'0': ('q4', '0', 'L')}
            self.dtm1.validate()

    def test_read_input_accepted(self):
        """Should return correct state if acceptable TM input is given."""
        final_config = self.dtm1.read_input('00001111')
        self.assertEqual(final_config[0], 'q4')
        self.assertEqual(str(final_config[1]), 'TMTape(\'xxxxyyyy..\', 9)')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dtm1.read_input_stepwise('00001111')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        self.assertEqual(configs[0][0], 'q0')
        self.assertEqual(str(configs[0][1]), 'TMTape(\'00001111\', 0)')
        self.assertEqual(configs[-1][0], 'q4')
        self.assertEqual(str(configs[-1][1]), 'TMTape(\'xxxxyyyy..\', 9)')

    def test_read_input_offset(self):
        """Should valdiate input when tape is offset."""
        final_config = self.dtm2.read_input('01010101')
        self.assertEqual(final_config[0], 'q4')
        self.assertEqual(str(final_config[1]), 'TMTape(\'yyx1010101\', 3)')

    def test_read_input_rejection(self):
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.dtm1.read_input('000011')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.dtm1.read_input('02')

    def test_accepts_input_true(self):
        """Should return False if DTM input is not accepted."""
        self.assertEqual(self.dtm1.accepts_input('00001111'), True)

    def test_accepts_input_false(self):
        """Should return False if DTM input is rejected."""
        self.assertEqual(self.dtm1.accepts_input('000011'), False)

    def test_transition_without_movement(self):
        """Tests transitions without movements."""
        dtm = DTM(
            # should accept 0^n1^n2^n for n >= 0
            input_symbols={'0', '1', '2'},
            tape_symbols={'0', '1', '2', '*', '.'},
            transitions={
                'q0': {
                    # replace one 0 with *
                    '0': ('q1', '*', 'N'),
                    '*': ('q0', '*', 'R'),
                    '.': ('qe', '.', 'N'),
                },
                'q1': {
                    # replace one 1 with *
                    '0': ('q1', '0', 'R'),
                    '1': ('q2', '*', 'N'),
                    '*': ('q1', '*', 'R'),
                },
                'q2': {
                    # replace one 2 with *
                    '1': ('q2', '1', 'R'),
                    '2': ('q3', '*', 'N'),
                    '*': ('q2', '*', 'R'),
                },
                'q3': {
                    # seek to end; assert that just 2's or *'s follow
                    '2': ('q3', '2', 'R'),
                    '*': ('q3', '*', 'R'),
                    '.': ('q4', '.', 'L'),
                },
                'q4': {
                    # seek to the beginning; checking if everything is *
                    '0': ('q5', '0', 'L'),
                    '1': ('q5', '1', 'L'),
                    '2': ('q5', '2', 'L'),
                    '*': ('q4', '*', 'L'),
                    '.': ('qe', '.', 'R'),
                },
                'q5': {
                    # seek to the beginning
                    '0': ('q5', '0', 'L'),
                    '1': ('q5', '1', 'L'),
                    '2': ('q5', '2', 'L'),
                    '*': ('q5', '*', 'L'),
                    '.': ('q0', '.', 'R'),
                }
            },
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'qe'},
            initial_state='q0',
            blank_symbol='.',
            final_states={'qe'},
        )
        self.assertTrue(dtm.accepts_input(''))
        self.assertTrue(dtm.accepts_input('012'))
        self.assertTrue(dtm.accepts_input('001122'))
        self.assertFalse(dtm.accepts_input('0'))
        self.assertFalse(dtm.accepts_input('01'))
        self.assertFalse(dtm.accepts_input('0112'))
        self.assertFalse(dtm.accepts_input('012012'))
