#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

# from unittest.mock import patch

import nose.tools as nose

import automata.pda.exceptions as pda_exceptions
import automata.base.exceptions as exceptions
import tests.test_pda as test_pda
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack


class TestDPDA(test_pda.TestPDA):
    """A test class for testing deterministic finite automata."""

    def test_init_dpda(self):
        """Should copy DPDA if passed into DPDA constructor."""
        new_dpda = DPDA(self.dpda)
        self.assert_is_copy(new_dpda, self.dpda)

    def test_init_dpda_missing_formal_params(self):
        """Should raise an error if formal DPDA parameters are missing."""
        with nose.assert_raises(TypeError):
            DPDA(
                states={'q0', 'q1', 'q2'},
                input_symbols={'a', 'b'},
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_self_invalid_input_symbol(self):
        """Should raise error if a transition has an invalid input symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['c'] = 'q2'
            self.dpda.validate_self()

    def test_validate_self_invalid_stack_symbol(self):
        """Should raise error if a transition has an invalid stack symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['a']['2'] = ('q1', ('1', '1'))
            self.dpda.validate_self()

    def test_validate_self_nondeterminism(self):
        """Should raise error if DPDA exhibits nondeterminism."""
        with nose.assert_raises(pda_exceptions.NondeterminismError):
            self.dpda.transitions['q2']['b']['0'] = ('q2', '0')
            self.dpda.validate_self()

    def test_validate_self_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dpda.initial_state = 'q4'
            self.dpda.validate_self()

    def test_validate_self_invalid_initial_stack_symbol(self):
        """Should raise error if the initial stack symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.initial_stack_symbol = '2'
            self.dpda.validate_self()

    def test_validate_self_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dpda.final_states = {'q4'}
            self.dpda.validate_self()

    def test_validate_input_valid_accept_by_final_state(self):
        """Should return correct config if DPDA accepts by final state."""
        nose.assert_equal(
            self.dpda.validate_input('aabb'), ('q3', PDAStack(['0'])))

    def test_validate_input_valid_accept_by_empty_stack(self):
        """Should return correct config if DPDA accepts by empty stack."""
        self.dpda.transitions['q2']['']['0'] = ('q2', '')
        nose.assert_equal(
            self.dpda.validate_input('aabb'), ('q2', PDAStack([])))

    def test_validate_input_valid_consecutive_lambda_transitions(self):
        """Should follow consecutive lambda transitions when validating."""
        self.dpda.states = {'q4'}
        self.dpda.final_states = {'q4'}
        self.dpda.transitions['q2']['']['0'] = ('q3', ('0',))
        self.dpda.transitions['q3'] = {
            '': {'0': ('q4', ('0',))}
        }
        nose.assert_equal(
            self.dpda.validate_input('aabb'), ('q4', PDAStack(['0'])))

    def test_validate_input_invalid_accept_by_final_state(self):
        """Should reject strings if DPDA accepts by final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.validate_input('aab')

    def test_validate_input_invalid_accept_by_empty_stack(self):
        """Should reject strings if DPDA accepts by empty stack."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.transitions['q2']['']['0'] = ('q2', '')
            self.dpda.validate_input('aab')

    def test_validate_input_invalid_undefined_transition(self):
        """Should reject strings which lead to an undefined transition."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.validate_input('01')

    def test_stack_copy(self):
        """Should create an exact of the PDA stack."""
        stack = PDAStack(['a', 'b'])
        stack_copy = stack.copy()
        nose.assert_is_not(stack, stack_copy)
        nose.assert_equal(stack, stack_copy)

    def test_stack_repr(self):
        """Should create proper string representation of PDA stack."""
        stack = PDAStack(['a', 'b'])
        nose.assert_equal(repr(stack), 'PDAStack([\'a\', \'b\'])')
