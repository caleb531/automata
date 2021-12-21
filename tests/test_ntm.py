#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NTMs."""

import types
from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.ntm import NTM
from automata.tm.tape import HeadDirection


class TestNTM(test_tm.TestTM):
    """A test class for testing nondeterministic Turing machines."""

    def test_init_ntm(self) -> None:
        """Should copy NTM if passed into NTM constructor."""
        new_dtm = NTM.copy(self.ntm1)
        self.assert_is_copy(new_dtm, self.ntm1)

    def test_init_ntm_missing_formal_params(self):
        """Should raise an error if formal NTM parameters are missing."""
        with nose.assert_raises(TypeError):
            NTM(
                states={'q0', 'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                tape_symbols={'0', '1', 'x', 'y', '.'},
                initial_state='q0',
                blank_symbol='.',
                final_states={'q4'}
            )

    @patch('automata.tm.ntm.NTM.validate')
    def test_init_validation(self, validate) -> None:
        """Should validate NTM when initialized."""
        NTM.copy(self.ntm1)
        validate.assert_called_once_with()

    def test_copy_ntm(self) -> None:
        """Should create exact copy of NTM if copy() method is called."""
        new_ntm = self.ntm1.copy()
        self.assert_is_copy(new_ntm, self.ntm1)

    def test_ntm_equal(self) -> None:
        """Should correctly determine if two NTMs are equal."""
        new_ntm = self.ntm1.copy()
        nose.assert_true(self.ntm1 == new_ntm, 'NTMs are not equal')

    def test_ntm_not_equal(self) -> None:
        """Should correctly determine if two NTMs are not equal."""
        new_ntm = self.ntm1.copy()
        new_ntm.final_states.add('q2')
        nose.assert_true(self.ntm1 != new_ntm, 'NTMs are equal')

    def test_validate_input_symbol_subset(self) -> None:
        """Should raise error if any input symbols are not tape symbols."""
        with nose.assert_raises(exceptions.MissingSymbolError):
            self.ntm1.input_symbols.add('3')
            self.ntm1.validate()

    def test_validate_invalid_transition_state(self) -> None:
        """Should raise error if a transition state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.ntm1.transitions['q4'] = self.ntm1.transitions['q0']
            self.ntm1.validate()

    def test_validate_invalid_transition_symbol(self) -> None:
        """Should raise error if a transition symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.ntm1.transitions['q0']['3'] = {('q0', '0', HeadDirection.R)}
            self.ntm1.validate()

    def test_validate_invalid_transition_result_state(self) -> None:
        """Should raise error if a transition result state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.ntm1.transitions['q0']['.'] = {('q4', '.', HeadDirection.R)}
            self.ntm1.validate()

    def test_validate_invalid_transition_result_symbol(self) -> None:
        """Should raise error if a transition result symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.ntm1.transitions['q0']['.'] = {('q3', '3', HeadDirection.R)}
            self.ntm1.validate()

    def test_validate_invalid_transition_result_direction(self) -> None:
        """Should raise error if a transition result direction is invalid."""
        with nose.assert_raises(tm_exceptions.InvalidDirectionError):
            self.ntm1.transitions['q0']['.'] = {('q3', '.', 'U')}
            self.ntm1.validate()

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.ntm1.initial_state = 'q4'
            self.ntm1.validate()

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.ntm1.transitions[self.ntm1.initial_state]
            self.ntm1.validate()

    def test_validate_nonfinal_initial_state(self) -> None:
        """Should raise error if the initial state is a final state."""
        with nose.assert_raises(exceptions.InitialStateError):
            self.ntm1.final_states.add('q0')
            self.ntm1.validate()

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.ntm1.final_states = {'q4'}
            self.ntm1.validate()

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.ntm1.final_states = {4}
            self.ntm1.validate()

    def test_validate_final_state_transitions(self) -> None:
        """Should raise error if a final state has any transitions."""
        with nose.assert_raises(exceptions.FinalStateError):
            self.ntm1.transitions['q3'] = {'0': {('q3', '0', HeadDirection.L)}}
            self.ntm1.validate()

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable TM input is given."""
        final_config = self.ntm1.read_input('00120001111').pop()
        nose.assert_equal(final_config[0], 'q3')
        nose.assert_equal(str(final_config[1]), 'TMTape(\'00120001111.\', 11)')

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.ntm1.read_input_stepwise('00120001111')
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        nose.assert_equal(first_config[0], 'q0')
        nose.assert_equal(str(first_config[1]), 'TMTape(\'00120001111\', 0)')
        last_config = configs[-1].pop()
        nose.assert_equal(last_config[0], 'q3')
        nose.assert_equal(str(last_config[1]), 'TMTape(\'00120001111.\', 11)')

    def test_read_input_rejection(self) -> None:
        """Should raise error if the machine halts."""
        with nose.assert_raises(exceptions.RejectionException):
            self.ntm1.read_input('0')

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.ntm1.read_input('02')

    def test_accepts_input_true(self) -> None:
        """Should return False if DTM input is not accepted."""
        nose.assert_equal(self.dtm1.accepts_input('00001111'), True)

    def test_accepts_input_false(self) -> None:
        """Should return False if DTM input is rejected."""
        nose.assert_equal(self.dtm1.accepts_input('000011'), False)
