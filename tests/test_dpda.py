#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

# from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack


class TestDPDA(test_pda.TestPDA):
    """A test class for testing deterministic finite automata."""

    def test_init_dpda(self) -> None:
        """Should copy DPDA if passed into DPDA constructor."""
        new_dpda = DPDA.copy(self.dpda)
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

    def test_init_dpda_no_acceptance_mode(self) -> None:
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
        nose.assert_equal(new_dpda.acceptance_mode, 'both')

    def test_init_dpda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with nose.assert_raises(pda_exceptions.InvalidAcceptanceModeError):
            self.dpda.acceptance_mode = 'foo'
            self.dpda.validate()

    def test_validate_invalid_input_symbol(self):
        """Should raise error if a transition has an invalid input symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['c'] = 'q2'
            self.dpda.validate()

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.transitions['q1']['a']['2'] = ('q1', ('1', '1'))
            self.dpda.validate()

    def test_validate_nondeterminism(self) -> None:
        """Should raise error if DPDA exhibits nondeterminism."""
        with nose.assert_raises(pda_exceptions.NondeterminismError):
            self.dpda.transitions['q2']['b']['0'] = ('q2', '0')
            self.dpda.validate()

    def test_read_input_rejected_nondeterministic_transition(self) -> None:
        """Should raise error if DPDA exhibits nondeterminism."""
        with nose.assert_raises(pda_exceptions.NondeterminismError):
            self.dpda.transitions['q2']['b']['0'] = ('q2', '0')
            self.dpda.read_input("abb")

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dpda.initial_state = 'q4'
            self.dpda.validate()

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dpda.initial_stack_symbol = '2'
            self.dpda.validate()

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dpda.final_states = {'q4'}
            self.dpda.validate()

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dpda.final_states = {4}
            self.dpda.validate()

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if DPDA accepts by final state."""
        nose.assert_equal(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q3', '', PDAStack(['0']))
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if DPDA accepts by empty stack."""
        self.dpda.acceptance_mode = 'empty_stack'
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.read_input('aabb')

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if DPDA accepts by empty stack."""
        self.dpda.transitions['q2']['']['0'] = ('q2', '')
        self.dpda.acceptance_mode = 'empty_stack'
        nose.assert_equal(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q2', '', PDAStack([]))
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if DPDA accepts by final state."""
        self.dpda.transitions['q2']['']['0'] = ('q2', '')
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.read_input('aabb')

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        self.dpda.states = {'q4'}
        self.dpda.final_states = {'q4'}
        self.dpda.transitions['q2']['']['0'] = ('q3', ('0',))
        self.dpda.transitions['q3'] = {
            '': {'0': ('q4', ('0',))}
        }
        nose.assert_equal(
            self.dpda.read_input('aabb'),
            PDAConfiguration('q4', '', PDAStack(['0']))
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if DPDA accepts by final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.read_input('aab')

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if DPDA accepts by empty stack."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.transitions['q2']['']['0'] = ('q2', '')
            self.dpda.read_input('aab')

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dpda.read_input('01')

    def test_accepts_input_true(self) -> None:
        """Should return False if DPDA input is not accepted."""
        nose.assert_equal(self.dpda.accepts_input('aabb'), True)

    def test_accepts_input_false(self) -> None:
        """Should return False if DPDA input is rejected."""
        nose.assert_equal(self.dpda.accepts_input('aab'), False)

    def test_empty_dpda(self) -> None:
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
        nose.assert_true(dpda.accepts_input(''))
