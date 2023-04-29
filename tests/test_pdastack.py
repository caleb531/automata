#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAStacks."""

import tests.test_pda as test_pda
from automata.pda.stack import PDAStack


class TestPDAStack(test_pda.TestPDA):
    """A test class for testing stacks of pushdown automata."""

    def test_stack_hashability(self):
        self.assertEqual(hash(PDAStack(["a", "b"])), hash(PDAStack(["a", "b"])))

    def test_stack_iter(self):
        """Should loop through the PDA stack in some manner."""
        self.assertEqual(list(PDAStack(["a", "b"])), ["a", "b"])

    def test_stack_repr(self):
        """Should create proper string representation of PDA stack."""
        stack = PDAStack(["a", "b"])
        self.assertEqual(repr(stack), "PDAStack(('a', 'b'))")
