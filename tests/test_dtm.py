#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import types

import nose.tools as nose

import turingmachines.tm as tm
import tests.test_tm as test_tm
from turingmachines.dtm import DTM


class TestDTM(test_tm.TestTM):
    """A test class for testing deterministic Turing machines."""

    def test_init_dtm(self):
        """Should copy DTM if passed into DTM constructor."""
        new_dtm = DTM(self.dtm1)
        nose.assert_is_not(new_dtm.states, self.dtm1.states)
        nose.assert_equal(new_dtm.states, self.dtm1.states)
        nose.assert_is_not(new_dtm.input_symbols, self.dtm1.input_symbols)
        nose.assert_equal(new_dtm.input_symbols, self.dtm1.input_symbols)
        nose.assert_is_not(new_dtm.tape_symbols, self.dtm1.tape_symbols)
        nose.assert_equal(new_dtm.tape_symbols, self.dtm1.tape_symbols)
        nose.assert_is_not(new_dtm.transitions, self.dtm1.transitions)
        nose.assert_equal(new_dtm.transitions, self.dtm1.transitions)
        nose.assert_equal(new_dtm.initial_state, self.dtm1.initial_state)
        nose.assert_equal(new_dtm.blank_symbol, self.dtm1.blank_symbol)
        nose.assert_is_not(new_dtm.final_states, self.dtm1.final_states)
        nose.assert_equal(new_dtm.final_states, self.dtm1.final_states)

    def test_validate_input_valid(self):
        """Should return correct stop state if valid TM input is given."""
        final_config = self.dtm1.validate_input('00001111')
        nose.assert_equal(final_config[0], 'q4')
        nose.assert_equal(str(final_config[1]), 'TMTape(\'xxxxyyyy.\')')

    def test_validate_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dtm1.validate_input('00001111', step=True)
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        configs = []
        for current_state, tape in validation_generator:
            configs.append((current_state, tape.copy()))
        nose.assert_equal(configs[0][0], 'q0')
        nose.assert_equal(str(configs[0][1]), 'TMTape(\'00001111\')')
        nose.assert_equal(configs[-1][0], 'q4')
        nose.assert_equal(str(configs[-1][1]), 'TMTape(\'xxxxyyyy.\')')

    def test_validate_input_offset(self):
        """Should valdiate input when tape is offset."""
        final_config = self.dtm2.validate_input('01010101')
        nose.assert_equal(final_config[0], 'q4')
        nose.assert_equal(str(final_config[1]), 'TMTape(\'yyx1010101\')')

    def test_validate_input_rejection(self):
        """Should raise error if the machine halts."""
        with nose.assert_raises(tm.RejectionError):
            self.dtm1.validate_input('000011')
