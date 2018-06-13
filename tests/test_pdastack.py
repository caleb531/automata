#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAStacks."""

# from unittest.mock import patch

import nose.tools as nose

import tests.test_pda as test_pda
from automata.pda.stack import PDAStack


class TestPDAStack(test_pda.TestPDA):
    """A test class for testing stacks of pushdown automata."""

    def test_stack_copy(self):
        """Should create an exact of the PDA stack."""
        stack = PDAStack(['a', 'b'])
        stack_copy = stack.copy()
        nose.assert_is(stack, stack_copy)
        nose.assert_equal(stack, stack_copy)

    def test_stack_iter(self):
        """Should loop through the PDA stack in some manner."""
        nose.assert_equal(list(PDAStack(['a', 'b'])), ['a', 'b'])

    def test_stack_repr(self):
        """Should create proper string representation of PDA stack."""
        stack = PDAStack(['a', 'b'])
        nose.assert_equal(repr(stack), 'PDAStack((\'a\', \'b\'))')
