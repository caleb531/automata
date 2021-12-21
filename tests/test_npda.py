#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NPDAs."""

# from unittest.mock import patch

import nose.tools as nose

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.npda import NPDA
from automata.pda.stack import PDAStack


class TestNPDA(test_pda.TestPDA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_npda(self) -> None:
        """Should copy NPDA if passed into NPDA constructor."""
        new_npda = NPDA.copy(self.npda)
        self.assert_is_copy(new_npda, self.npda)

    def test_init_npda_missing_formal_params(self):
        """Should raise an error if formal NPDA parameters are missing."""
        with nose.assert_raises(TypeError):
            NPDA(
                states={'q0', 'q1', 'q2'},
                input_symbols={'a', 'b'},
                initial_state='q0',
                final_states={'q0'}
            )

    def test_init_npda_no_acceptance_mode(self) -> None:
        """Should create a new NPDA."""
        new_npda = NPDA(
            states={'q0'},
            input_symbols={'a', 'b'},
            stack_symbols={'#'},
            transitions={
                'q0': {
                    'a': {'#': {('q0', '')}},
                }
            },
            initial_state='q0',
            initial_stack_symbol='#',
            final_states={'q0'}
        )
        nose.assert_equal(new_npda.acceptance_mode, 'both')

    def test_init_npda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with nose.assert_raises(pda_exceptions.InvalidAcceptanceModeError):
            self.npda.acceptance_mode = 'foo'
            self.npda.validate()

    def test_validate_invalid_input_symbol(self) -> None:
        """Should raise error if a transition has an invalid input symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.npda.transitions['q1']['c'] = 'q2'
            self.npda.validate()

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.npda.transitions['q1']['a']['2'] = {('q1', ('1', '1'))}
            self.npda.validate()

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.npda.initial_state = 'q4'
            self.npda.validate()

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.npda.initial_stack_symbol = '2'
            self.npda.validate()

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.npda.final_states = {'q4'}
            self.npda.validate()

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.npda.final_states = {4}
            self.npda.validate()

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if NPDA accepts by final state."""
        nose.assert_equal(
            self.npda.read_input('abaaba'),
            {PDAConfiguration('q2', '', PDAStack(['#']))}
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if NPDA accepts by empty stack."""
        self.npda.acceptance_mode = 'empty_stack'
        with nose.assert_raises(exceptions.RejectionException):
            self.npda.read_input('abaaba'),

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if NPDA accepts by empty stack."""
        self.npda.transitions['q2'] = {'': {'#': {('q2', '')}}}
        self.npda.final_states = set()
        self.npda.acceptance_mode = 'empty_stack'
        nose.assert_equal(
            self.npda.read_input('abaaba'),
            {PDAConfiguration('q2', '', PDAStack([]))}
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if NPDA accepts by final state."""
        self.npda.acceptance_mode = 'final_state'
        self.npda.states.add('q3')
        self.npda.transitions['q1'][''] = {'#': {('q3', '')}}
        with nose.assert_raises(exceptions.RejectionException):
            self.npda.read_input('abaaba')

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        self.npda.states.update({'q3', 'q4'})
        self.npda.final_states = {'q4'}
        self.npda.transitions['q2'] = {'': {'#': {('q3', '#')}}}
        self.npda.transitions['q3'] = {'': {'#': {('q4', '#')}}}
        nose.assert_equal(
            self.npda.read_input('abaaba'),
            {PDAConfiguration('q4', '', PDAStack(['#']))}
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if NPDA accepts by final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.npda.read_input('aaba')

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if NPDA accepts by empty stack."""
        self.npda.transitions['q2'] = {'': {'#': {('q2', '')}}}
        self.npda.final_states = set()
        with nose.assert_raises(exceptions.RejectionException):
            self.npda.read_input('aaba')

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with nose.assert_raises(exceptions.RejectionException):
            self.npda.read_input('01')

    def test_accepts_input_true(self) -> None:
        """Should return True if NPDA input is accepted."""
        nose.assert_equal(self.npda.accepts_input('abaaba'), True)

    def test_accepts_input_false(self) -> None:
        """Should return False if NPDA input is rejected."""
        nose.assert_equal(self.npda.accepts_input('aaba'), False)
