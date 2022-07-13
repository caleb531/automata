#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

# from unittest.mock import patch

import unittest

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack


class TestDPDA(test_pda.TestPDA):
    """A test class for testing deterministic finite automata."""

    def test_init_dpda(self):
        """Should copy DPDA if passed into DPDA constructor."""
        new_dpda = DPDA.copy(self.dpda)
        self.assert_is_copy(new_dpda, self.dpda)

    def test_init_dpda_missing_formal_params(self):
        """Should raise an error if formal DPDA parameters are missing."""
        with self.assertRaises(TypeError):
            DPDA(
                states={'q0', 'q1', 'q2'},
                input_symbols={'a', 'b'},
                initial_state='q0',
                final_states={'q0'}
            )

    def test_init_dpda_no_acceptance_mode(self):
        """Should create a new DPDA."""
        new_dpda = DPDA(
            states={'q0'},
            input_symbols={'a', 'b'},
            stack_symbols={'#'},
            transitions={
                'q0': {
                    'a': {'#': ('q0', '')},
                }
            },
            initial_state='q0',
            initial_stack_symbol='#',
            final_states={'q0'}
        )
        self.assertEqual(new_dpda.acceptance_mode, 'both')

    def test_init_dpda_invalid_acceptance_mode(self):
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with self.assertRaises(pda_exceptions.InvalidAcceptanceModeError):
            self.dpda.acceptance_mode = 'foo'
            self.dpda.validate()

    def test_validate_invalid_input_symbol(self):
        """Should raise error if a transition has an invalid input symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['c'] = 'q2'
            self.dpda.validate()

    def test_validate_invalid_stack_symbol(self):
        """Should raise error if a transition has an invalid stack symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['a']['2'] = ('q1', ('1', '1'))
            self.dpda.validate()

    def test_validate_nondeterminism(self):
        """Should raise error if DPDA exhibits nondeterminism."""
        with self.assertRaises(pda_exceptions.NondeterminismError):
            self.dpda.transitions['q2']['b']['0'] = ('q2', '0')
            self.dpda.validate()

    def test_read_input_rejected_nondeterministic_transition(self):
        """Should raise error if DPDA exhibits nondeterminism."""
        with self.assertRaises(pda_exceptions.NondeterminismError):
            self.dpda.transitions['q2']['b']['0'] = ('q2', '0')
            self.dpda.read_input("abb")

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dpda.initial_state = 'q4'
            self.dpda.validate()

    def test_validate_invalid_initial_stack_symbol(self):
        """Should raise error if the initial stack symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dpda.initial_stack_symbol = '2'
            self.dpda.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dpda.final_states = {'q4'}
            self.dpda.validate()

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.dpda.final_states = {4}
            self.dpda.validate()

    def test_read_input_valid_accept_by_final_state(self):
        """Should return correct config if DPDA accepts by final state."""
        self.assertEqual(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q3', '', PDAStack(['0']))
        )

    def test_read_input_invalid_accept_by_final_state(self):
        """Should not accept by final state if DPDA accepts by empty stack."""
        self.dpda.acceptance_mode = 'empty_stack'
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input('aabb')

    def test_read_input_valid_accept_by_empty_stack(self):
        """Should return correct config if DPDA accepts by empty stack."""
        self.dpda.transitions['q2']['']['0'] = ('q2', '')
        self.dpda.acceptance_mode = 'empty_stack'
        self.assertEqual(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q2', '', PDAStack([]))
        )

    def test_read_input_invalid_accept_by_empty_stack(self):
        """Should not accept by empty stack if DPDA accepts by final state."""
        self.dpda.transitions['q2']['']['0'] = ('q2', '')
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input('aabb')

    def test_read_input_valid_consecutive_lambda_transitions(self):
        """Should follow consecutive lambda transitions when validating."""
        self.dpda.states = {'q4'}
        self.dpda.final_states = {'q4'}
        self.dpda.transitions['q2']['']['0'] = ('q3', ('0',))
        self.dpda.transitions['q3'] = {
            '': {'0': ('q4', ('0',))}
        }
        self.assertEqual(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q4', '', PDAStack(['0']))
        )

    def test_read_input_rejected_accept_by_final_state(self):
        """Should reject strings if DPDA accepts by final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input('aab')

    def test_read_input_rejected_accept_by_empty_stack(self):
        """Should reject strings if DPDA accepts by empty stack."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.transitions['q2']['']['0'] = ('q2', '')
            self.dpda.read_input('aab')

    def test_read_input_rejected_undefined_transition(self):
        """Should reject strings which lead to an undefined transition."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input('01')

    def test_accepts_input_true(self):
        """Should return False if DPDA input is not accepted."""
        self.assertEqual(self.dpda.accepts_input('aabb'), True)

    def test_accepts_input_false(self):
        """Should return False if DPDA input is rejected."""
        self.assertEqual(self.dpda.accepts_input('aab'), False)

    def test_empty_dpda(self):
        """Should accept an empty input if the DPDA is empty."""
        dpda = DPDA(
            states={'q0'},
            input_symbols=set(),
            stack_symbols={'0'},
            transitions=dict(),
            initial_state='q0',
            initial_stack_symbol='0',
            final_states={'q0'},
            acceptance_mode='both'
        )
        self.assertTrue(dpda.accepts_input(''))
