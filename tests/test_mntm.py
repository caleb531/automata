#!/usr/bin/env python3
"""Classes and functions for testing the behavior of MNTMs."""

import math
import random
import types
from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import tests.test_tm as test_tm
from automata.tm.mntm import MNTM


class TestMNTM(test_tm.TestTM):
    """A test class for testing multitape nondeterministic Turing machines."""

    def test_init_mntm(self):
        """Should copy MNTM if passed into MNTM constructor."""
        new_mntm = MNTM.copy(self.mntm1)
        self.assert_is_copy(new_mntm, self.mntm1)

    def test_init_mntm_missing_formal_params(self):
        """Should raise an error if formal MNTM parameters are missing."""
        with nose.assert_raises(TypeError):
            MNTM(
                states={'q0', 'q1', 'q2', 'q3', 'q4'},
                input_symbols={'0', '1'},
                tape_symbols={'0', '1', 'x', 'y', '.'},
                initial_state='q0',
                blank_symbol='.',
                final_states={'q4'}
            )

    @patch('automata.tm.mntm.MNTM.validate')
    def test_init_validation(self, validate):
        """Should validate MNTM when initialized."""
        MNTM.copy(self.mntm1)
        validate.assert_called_once_with()

    def test_copy_ntm(self):
        """Should create exact copy of MNTM if copy() method is called."""
        new_mntm = self.mntm1.copy()
        self.assert_is_copy(new_mntm, self.mntm1)

    def test_ntm_equal(self):
        """Should correctly determine if two MNTMs are equal."""
        new_mntm = self.mntm1.copy()
        nose.assert_true(self.mntm1 == new_mntm, 'MNTMs are not equal')

    def test_ntm_not_equal(self):
        """Should correctly determine if two MNTMs are not equal."""
        new_mntm = self.mntm1.copy()
        new_mntm.final_states.add('q2')
        nose.assert_true(self.mntm1 != new_mntm, 'MNTMs are equal')

    def test_validate_input_symbol_subset(self):
        """Should raise error if any input symbols are not tape symbols."""
        with nose.assert_raises(exceptions.MissingSymbolError):
            self.mntm1.input_symbols.add('3')
            self.mntm1.validate()

    def test_validate_invalid_transition_state(self):
        """Should raise error if a transition state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.mntm1.transitions['q4'] = self.mntm1.transitions['q0']
            self.mntm1.validate()

    def test_validate_invalid_transition_symbol(self):
        """Should raise error if a transition symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.mntm1.transitions['q0'][("2", "#")] = [
                ('q1', (('#', 'R'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_state(self):
        """Should raise error if a transition result state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q3', (('#', 'L'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_symbol(self):
        """Should raise error if a transition result symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q1', (('.', 'U'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_direction(self):
        """Should raise error if a transition result direction is invalid."""
        with nose.assert_raises(tm_exceptions.InvalidDirectionError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q1', (('#', 'U'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.mntm1.initial_state = 'q4'
            self.mntm1.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.mntm1.transitions[self.mntm1.initial_state]
            self.mntm1.validate()

    def test_validate_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with nose.assert_raises(exceptions.InitialStateError):
            self.mntm1.final_states.add('q0')
            self.mntm1.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.mntm1.final_states = {'q4'}
            self.mntm1.validate()

    def test_validate_final_state_transitions(self):
        """Should raise error if a final state has any transitions."""
        with nose.assert_raises(exceptions.FinalStateError):
            self.mntm1.transitions['q1'] = {('0', '#'): [
                ('q0', (('0', 'L'), ('0', 'R')))]
            }
            self.mntm1.validate()

    def test_validate_tapes_consistency(self):
        with nose.assert_raises(exceptions.InconsistentTapesException):
            self.mntm1.n_tapes = 3
            self.mntm1.validate()
        self.mntm1.n_tapes = 2
        with nose.assert_raises(exceptions.InconsistentTapesException):
            self.mntm1.transitions["q0"][("0", "#")] = [(
                "q0", (("0", "R"), ("#", "N"), ("#", "R")))]
            self.mntm1.validate()

    def test_get_next_configuration(self):
        subtm = self.mntm1._get_next_configuration(("q0", (
            ("0", "R"), ("#", "N"))))
        nose.assert_equal(str(subtm.tapes[0]), 'TMTape(\'0#\', 1)',
                          'TMTape(\'#\', 0)')

    def test_read_extended_tape(self):
        pass  # TODO

    def test_simulate_as_ntm(self):
        pass  # TODO

    def test_read_input_accepted(self):
        """Should return correct state if acceptable TM input is given."""
        final_config = self.mntm1.read_input('0101101011').pop()
        nose.assert_equal(final_config[0], 'q1')
        nose.assert_equal(
            str(final_config[1][0]),
            'TMTape(\'0101101011#\', 10)')
        nose.assert_equal(str(final_config[1][1]), 'TMTape(\'111111#\', 6)')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.mntm1.read_input_stepwise('0010101111')
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        nose.assert_equal(first_config[0], 'q0')
        nose.assert_equal(str(first_config[1][0]), 'TMTape(\'0010101111\', 0)')
        nose.assert_equal(str(first_config[1][1]), 'TMTape(\'#\', 0)')
        last_config = configs[-1].pop()
        nose.assert_equal(last_config[0], 'q1')
        nose.assert_equal(
            str(last_config[1][0]),
            'TMTape(\'0010101111#\', 10)')
        nose.assert_equal(str(last_config[1][1]), 'TMTape(\'111111#\', 6)')

    def test_read_input_rejection(self):
        """Should raise error if the machine halts."""
        with nose.assert_raises(exceptions.RejectionException):
            self.mntm1.read_input('2')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.mntm2.read_input('1')

    def test_accepts_input_true(self):
        """Should return False if MNTM input is not accepted."""
        test_limit = 20
        for i in range(test_limit):
            input_str_1 = ""
            input_str_2 = "#0"
            input_str_3 = "1"
            for _ in range(i):
                k = random.randint(0, 1)
                input_str_1 += str(k)
                input_str_2 += "0"
                input_str_3 += str(k)

            input_str_3 += input_str_3
            # Should accept all
            nose.assert_equal(self.mntm1.accepts_input(input_str_1), True)
            nose.assert_equal(self.mntm3.accepts_input(input_str_3), True)

            # Should not accept because this would not be of the form ww
            nose.assert_equal(self.mntm3.accepts_input(
                input_str_3 + str(random.randint(0, 1))), False)

            # Should accept only if input string's length is a perfect square
            if self.is_perfect_square(len(input_str_2) - 1):
                nose.assert_equal(self.mntm2.accepts_input(input_str_2), True)
            else:
                nose.assert_equal(self.mntm2.accepts_input(input_str_2), False)

    def test_accepts_input_false(self):
        """Should return False if MNTM input is rejected."""
        nose.assert_equal(self.mntm1.accepts_input('000012'), False)
        nose.assert_equal(self.mntm2.accepts_input('#00000'), False)

    @staticmethod
    def is_perfect_square(number: int):
        return number == int(math.sqrt(number)) ** 2
