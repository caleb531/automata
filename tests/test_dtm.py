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
        self.assert_is_copy(new_dtm, self.dtm1)

    def test_copy_dtm(self):
        """Should create exact copy of DTM if copy() method is called."""
        new_dtm = self.dtm1.copy()
        self.assert_is_copy(new_dtm, self.dtm1)

    def test_dtm_equal(self):
        """Should correctly determine if two DTMs are equal."""
        new_dtm = self.dtm1.copy()
        nose.assert_true(self.dtm1 == new_dtm, 'DTMs are not equal')

    def test_dtm_not_equal(self):
        """Should correctly determine if two DTMs are not equal."""
        new_dtm = self.dtm1.copy()
        new_dtm.final_states.add('q2')
        nose.assert_true(self.dtm1 != new_dtm, 'DTMs are equal')

    def test_validate_self_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(tm.InvalidStateError):
            self.dtm1.initial_state = 'q5'
            self.dtm1.validate_self()

    def test_validate_self_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(tm.InvalidStateError):
            self.dtm1.final_states = {'q5'}
            self.dtm1.validate_self()

    def test_validate_self_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with nose.assert_raises(tm.FinalStateError):
            self.dtm1.final_states.add('q0')
            self.dtm1.validate_self()

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
