#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NTMs."""

import types
from unittest.mock import patch

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.ntm import NTM


class TestNTM(test_tm.TestTM):
    """A test class for testing nondeterministic Turing machines."""

    def test_init_ntm(self):
        """Should copy NTM if passed into NTM constructor."""
        new_dtm = self.ntm1.copy()
        self.assertIsNot(new_dtm, self.ntm1)

    def test_init_ntm_missing_formal_params(self):
        """Should raise an error if formal NTM parameters are missing."""
        with self.assertRaises(TypeError):
            NTM(
                states={'q0', 'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                tape_symbols={'0', '1', 'x', 'y', '.'},
                initial_state='q0',
                blank_symbol='.',
                final_states={'q4'}
            )

    @patch('automata.tm.ntm.NTM.validate')
    def test_init_validation(self, validate):
        """Should validate NTM when initialized."""
        NTM.copy(self.ntm1)
        validate.assert_called_once_with()

    def test_copy_ntm(self):
        """Should create exact copy of NTM if copy() method is called."""
        new_ntm = self.ntm1.copy()
        self.assertIsNot(new_ntm, self.ntm1)

    def test_validate_input_symbol_subset(self):
        """Should raise error if input symbols are not a strict superset of tape symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_transition_state(self):
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}},
                    'q4': {'0': {('q1', '0', 'R')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_transition_symbol(self):
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}, '3': {('q0', '0' 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_transition_result_state(self):
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}, '.': {('q4', '.', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_transition_result_symbol(self):
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}, '.': {('q2', '5', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_transition_result_direction(self):
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'U')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q5',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_validate_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q0'}
            )

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q5'}
            )

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={5}
            )

    def test_validate_final_state_transitions(self):
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            NTM(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0'},
                tape_symbols={'0', '.'},
                transitions={
                    'q0': {'0': {('q1', '0', 'R')}},
                    'q1': {'0': {('q2', '0', 'L')}},
                    'q2': {'0': {('q1', '0', 'L')}}
                },
                initial_state='q0',
                blank_symbol='.',
                final_states={'q2'}
            )

    def test_read_input_accepted(self):
        """Should return correct state if acceptable TM input is given."""
        final_config = self.ntm1.read_input('00120001111').pop()
        self.assertEqual(final_config[0], 'q3')
        self.assertEqual(str(final_config[1]), 'TMTape(\'00120001111.\', 11)')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.ntm1.read_input_stepwise('00120001111')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config[0], 'q0')
        self.assertEqual(str(first_config[1]), 'TMTape(\'00120001111\', 0)')
        last_config = configs[-1].pop()
        self.assertEqual(last_config[0], 'q3')
        self.assertEqual(str(last_config[1]), 'TMTape(\'00120001111.\', 11)')

    def test_read_input_rejection(self):
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.ntm1.read_input('0')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.ntm1.read_input('02')

    def test_accepts_input_true(self):
        """Should return False if DTM input is not accepted."""
        self.assertEqual(self.dtm1.accepts_input('00001111'), True)

    def test_accepts_input_false(self):
        """Should return False if DTM input is rejected."""
        self.assertEqual(self.dtm1.accepts_input('000011'), False)
