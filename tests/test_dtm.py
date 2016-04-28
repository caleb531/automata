#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import types

import nose.tools as nose

import turingmachines.tm as tm
from turingmachines.dtm import DTM


class TestDTM(object):
    """A test class for testing deterministic Turing machines."""

    def setup(self):
        """Reset test machines before every test function."""
        # TM which matches all strings beginning with '0's, and followed by the
        # same number of '1's
        self.dtm1 = DTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', 'x', 'y', '.'},
            transitions={
                'q0': {
                    '0': ('q1', 'x', 'R'),
                    'y': ('q3', 'y', 'R')
                },
                'q1': {
                    '0': ('q1', '0', 'R'),
                    '1': ('q2', 'y', 'L'),
                    'y': ('q1', 'y', 'R')
                },
                'q2': {
                    '0': ('q2', '0', 'L'),
                    'x': ('q0', 'x', 'R'),
                    'y': ('q2', 'y', 'L')
                },
                'q3': {
                    'y': ('q3', 'y', 'R'),
                    '.': ('q4', '.', 'R')
                }
            },
            initial_state='q0',
            blank_symbol='.',
            final_states={'q4'}
        )
        # TM which matches any binary string, but is designed to test the
        # tape's position offsetting algorithm
        self.dtm2 = DTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', 'x', 'y', '.'},
            transitions={
                'q0': {
                    '0': ('q1', 'x', 'L')
                },
                'q1': {
                    '.': ('q2', 'y', 'L')
                },
                'q2': {
                    '.': ('q3', 'y', 'R')
                },
                'q3': {
                    'y': ('q3', 'y', 'R'),
                    'x': ('q4', 'x', 'R')
                }
            },
            initial_state='q0',
            blank_symbol='.',
            final_states={'q4'}
        )

    def test_init_dtm(self):
        """Should copy DTM if passed into DTM constructor."""
        new_dtm = DTM(self.dtm1)
        nose.assert_is_not(new_dtm.states, self.dtm1.states)
        nose.assert_equal(new_dtm.states, self.dtm1.states)
        nose.assert_is_not(new_dtm.input_symbols, self.dtm1.input_symbols)
        nose.assert_equal(new_dtm.input_symbols, self.dtm1.input_symbols)
        nose.assert_is_not(new_dtm.transitions, self.dtm1.transitions)
        nose.assert_equal(new_dtm.transitions, self.dtm1.transitions)
        nose.assert_equal(new_dtm.initial_state, self.dtm1.initial_state)
        nose.assert_is_not(new_dtm.final_states, self.dtm1.final_states)
        nose.assert_equal(new_dtm.final_states, self.dtm1.final_states)

    def test_validate_input_valid(self):
        """Should return correct stop state if valid TM input is given."""
        final_config = self.dtm1.validate_input('00001111')
        nose.assert_equal(final_config[0], 'q4')
        nose.assert_equal(str(final_config[1]), 'xxxxyyyy.')

    def test_validate_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dtm1.validate_input('00001111', step=True)
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        configs = []
        for current_state, tape in validation_generator:
            configs.append((current_state, tape.copy()))
        nose.assert_equal(configs[0][0], 'q0')
        nose.assert_equal(str(configs[0][1]), '00001111')
        nose.assert_equal(configs[-1][0], 'q4')
        nose.assert_equal(str(configs[-1][1]), 'xxxxyyyy.')

    def test_validate_input_offset(self):
        """Should valdiate input when tape is offset."""
        final_config = self.dtm2.validate_input('01010101')
        nose.assert_equal(final_config[0], 'q4')
        nose.assert_equal(str(final_config[1]), 'yyx1010101')

    def test_validate_input_rejection(self):
        """Should raise error if the machine halts."""
        with nose.assert_raises(tm.HaltError):
            self.dtm1.validate_input('000011')
