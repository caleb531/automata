#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.dtm import DTM


class TestDTM(test_tm.TestTM):
    """A test class for testing deterministic Turing machines."""

    def test_init_dtm(self):
        """Should copy DTM if passed into DTM constructor."""
        new_dtm = DTM(self.dtm1)
        self.assert_is_copy(new_dtm, self.dtm1)

    def test_init_dtm_missing_formal_params(self):
        """Should raise an error if formal DTM parameters are missing."""
        with nose.assert_raises(TypeError):
            DTM(
                states={'q0', 'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                tape_symbols={'0', '1', 'x', 'y', '.'},
                initial_state='q0',
                blank_symbol='.',
                final_states={'q4'}
            )

    @patch('automata.tm.dtm.DTM.validate_self')
    def test_init_validation(self, validate_self):
        """Should validate DTM when initialized."""
        DTM(self.dtm1)
        validate_self.assert_called_once_with()

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

    def test_validate_self_input_symbol_subset(self):
        """Should raise error if any input symbols are not tape symbols."""
        with nose.assert_raises(exceptions.MissingSymbolError):
            self.dtm1.input_symbols.add('2')
            self.dtm1.validate_self()

    def test_validate_self_invalid_transition_state(self):
        """Should raise error if a transition state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dtm1.transitions['q5'] = self.dtm1.transitions['q0']
            self.dtm1.validate_self()

    def test_validate_self_invalid_transition_symbol(self):
        """Should raise error if a transition symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dtm1.transitions['q0']['2'] = ('q0', '0' 'R')
            self.dtm1.validate_self()

    def test_validate_self_invalid_transition_result_state(self):
        """Should raise error if a transition result state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dtm1.transitions['q0']['y'] = ('q5', 'y', 'R')
            self.dtm1.validate_self()

    def test_validate_self_invalid_transition_result_symbol(self):
        """Should raise error if a transition result symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dtm1.transitions['q0']['y'] = ('q3', 'z', 'R')
            self.dtm1.validate_self()

    def test_validate_self_invalid_transition_result_direction(self):
        """Should raise error if a transition result direction is invalid."""
        with nose.assert_raises(tm_exceptions.InvalidDirectionError):
            self.dtm1.transitions['q0']['y'] = ('q3', 'y', 'U')
            self.dtm1.validate_self()

    def test_validate_self_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dtm1.initial_state = 'q5'
            self.dtm1.validate_self()

    def test_validate_self_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.dtm1.transitions[self.dtm1.initial_state]
            self.dtm1.validate_self()

    def test_validate_self_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with nose.assert_raises(exceptions.InitialStateError):
            self.dtm1.final_states.add('q0')
            self.dtm1.validate_self()

    def test_validate_self_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dtm1.final_states = {'q5'}
            self.dtm1.validate_self()

    def test_validate_self_final_state_transitions(self):
        """Should raise error if a final state has any transitions."""
        with nose.assert_raises(exceptions.FinalStateError):
            self.dtm1.transitions['q4'] = {'0': ('q4', '0', 'L')}
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
        with nose.assert_raises(exceptions.RejectionException):
            self.dtm1.validate_input('000011')

    def test_validate_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dtm1.validate_input('02')
