#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

# from unittest.mock import patch

import nose.tools as nose

import automata.shared.exceptions as exceptions
import tests.test_pda as test_pda
from automata.pda.dpda import DPDA


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

    def test_validate_input_valid(self):
        """Should return correct configuration if valid DPDA input is given."""
        # nose.assert_equal(self.dpda.validate_input('aabb'), ('q3', ['0']))
