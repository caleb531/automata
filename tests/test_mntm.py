#!/usr/bin/env python3
"""Classes and functions for testing the behavior of MNTMs."""

import math
import random
import types
from unittest.mock import patch

import unittest

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
        with self.assertRaises(TypeError):
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
        self.assertTrue(self.mntm1 == new_mntm, 'MNTMs are not equal')

    def test_ntm_not_equal(self):
        """Should correctly determine if two MNTMs are not equal."""
        new_mntm = self.mntm1.copy()
        new_mntm.final_states.add('q2')
        self.assertTrue(self.mntm1 != new_mntm, 'MNTMs are equal')

    def test_validate_input_symbol_subset(self):
        """Should raise error if any input symbols are not tape symbols."""
        with self.assertRaises(exceptions.MissingSymbolError):
            self.mntm1.input_symbols.add('3')
            self.mntm1.validate()

    def test_validate_invalid_transition_state(self):
        """Should raise error if a transition state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.mntm1.transitions['q4'] = self.mntm1.transitions['q0']
            self.mntm1.validate()

    def test_validate_invalid_transition_symbol(self):
        """Should raise error if a transition symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.mntm1.transitions['q0'][("2", "#")] = [
                ('q1', (('#', 'R'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_state(self):
        """Should raise error if a transition result state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q3', (('#', 'L'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_symbol(self):
        """Should raise error if a transition result symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q1', (('.', 'U'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_transition_result_direction(self):
        """Should raise error if a transition result direction is invalid."""
        with self.assertRaises(tm_exceptions.InvalidDirectionError):
            self.mntm1.transitions['q0'][("1", "#")] = [
                ('q1', (('#', 'U'), ('#', 'R')))]
            self.mntm1.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.mntm1.initial_state = 'q4'
            self.mntm1.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            del self.mntm1.transitions[self.mntm1.initial_state]
            self.mntm1.validate()

    def test_validate_nonfinal_initial_state(self):
        """Should raise error if the initial state is a final state."""
        with self.assertRaises(exceptions.InitialStateError):
            self.mntm1.final_states.add('q0')
            self.mntm1.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.mntm1.final_states = {'q4'}
            self.mntm1.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.mntm1.final_states = {4}
            self.mntm1.validate()

    def test_validate_final_state_transitions(self):
        """Should raise error if a final state has any transitions."""
        with self.assertRaises(exceptions.FinalStateError):
            self.mntm1.transitions['q1'] = {('0', '#'): [
                ('q0', (('0', 'L'), ('0', 'R')))]
            }
            self.mntm1.validate()

    def test_validate_tapes_consistency(self):
        with self.assertRaises(tm_exceptions.InconsistentTapesException):
            self.mntm1.n_tapes = 3
            self.mntm1.validate()
        self.mntm1.n_tapes = 2
        with self.assertRaises(tm_exceptions.InconsistentTapesException):
            self.mntm1.transitions["q0"][("0", "#")] = [(
                "q0", (("0", "R"), ("#", "N"), ("#", "R")))]
            self.mntm1.validate()

    def test_get_next_configuration(self):
        subtm = self.mntm1._get_next_configuration(("q0", (
            ("0", "R"), ("#", "N"))))
        self.assertEqual(str(subtm.tapes[0]), 'TMTape(\'0#\', 1)',
                          'TMTape(\'#\', 0)')

    def test_read_extended_tape(self):
        self.assertEqual(self.mntm1._read_extended_tape(
            '10^10_1^00_00#^_', '^'), ('0', '1', '#'))
        self.assertEqual(self.mntm1._read_extended_tape(
            '1.10_1.00_0.#_', '.'), ('1', '1', '0'))
        self.assertEqual(self.mntm1._read_extended_tape(
            '10#^_00#^_00^_', '^'), ('#', '#', '0'))

        with self.assertRaisesRegex(tm_exceptions.MalformedExtendedTapeError,
                                      "head symbol was found on leftmost " +
                                      "end of the extended tape"):
            self.assertEqual(self.mntm1._read_extended_tape(
                '^10#_1^010#_00^', '^'), ('', '1', '0'))

        with self.assertRaisesRegex(tm_exceptions.MalformedExtendedTapeError,
                                      "no head symbol found on one of the " +
                                      "virtual tapes"):
            self.assertEqual(self.mntm1._read_extended_tape(
                '0^10#_1010#_00^_', '^'), ('0', '', '0'))

        with self.assertRaisesRegex(tm_exceptions.MalformedExtendedTapeError,
                                      "there must be 1 virtual head for " +
                                      "every tape separator symbol"):
            self.assertEqual(self.mntm1._read_extended_tape(
                '0^1010^10#^', '^'), ('0', '0', '#'))

        with self.assertRaisesRegex(tm_exceptions.MalformedExtendedTapeError,
                                      "more than one head symbol found on " +
                                      "one of the virtual tapes"):
            self.assertEqual(self.mntm1._read_extended_tape(
                '0^101010^_#^_', '^'), ('0', '0', '#'))

    def test_read_input_as_ntm(self):
        validation_generator = self.mntm2.read_input_as_ntm('#0000')
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config[0], 'q-1')
        self.assertEqual(str(first_config[1]), 'TMTape(\'#^0000_#^_#^_\', 0)')
        last_config = configs[-1].pop()
        self.assertEqual(last_config[0], 'qf')
        self.assertEqual(str(last_config[1]),
                          'TMTape(\'#0000#^_#0000#^_#XYYY#^_\', 23)')

        with self.assertRaises(exceptions.RejectionException):
            for _ in self.mntm2.read_input_as_ntm('#00'):
                pass

    def test_read_input_accepted(self):
        """Should return correct state if acceptable TM input is given."""
        final_config = self.mntm1.read_input('0101101011').pop()
        self.assertEqual(final_config[0], 'q1')
        self.assertEqual(
            str(final_config[1][0]),
            'TMTape(\'0101101011#\', 10)')
        self.assertEqual(str(final_config[1][1]), 'TMTape(\'111111#\', 6)')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.mntm1.read_input_stepwise('0010101111')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config[0], 'q0')
        self.assertEqual(str(first_config[1][0]), 'TMTape(\'0010101111\', 0)')
        self.assertEqual(str(first_config[1][1]), 'TMTape(\'#\', 0)')
        last_config = configs[-1].pop()
        self.assertEqual(last_config[0], 'q1')
        self.assertEqual(
            str(last_config[1][0]),
            'TMTape(\'0010101111#\', 10)')
        self.assertEqual(str(last_config[1][1]), 'TMTape(\'111111#\', 6)')

    def test_read_input_rejection(self):
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.mntm1.read_input('2')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
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
            self.assertEqual(self.mntm1.accepts_input(input_str_1), True)
            self.assertEqual(self.mntm3.accepts_input(input_str_3), True)

            # Should not accept because this would not be of the form ww
            self.assertEqual(self.mntm3.accepts_input(
                input_str_3 + str(random.randint(0, 1))), False)

            # Should accept only if input string's length is a perfect square
            if self.is_perfect_square(len(input_str_2) - 1):
                self.assertEqual(self.mntm2.accepts_input(input_str_2), True)
            else:
                self.assertEqual(self.mntm2.accepts_input(input_str_2), False)

    def test_accepts_input_false(self):
        """Should return False if MNTM input is rejected."""
        self.assertEqual(self.mntm1.accepts_input('000012'), False)
        self.assertEqual(self.mntm2.accepts_input('#00000'), False)

    @staticmethod
    def is_perfect_square(number: int):
        return number == int(math.sqrt(number)) ** 2
