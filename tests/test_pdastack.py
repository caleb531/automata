#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAStacks."""

import tests.test_pda as test_pda
from automata.pda.stack import PDAStack


class TestPDAStack(test_pda.TestPDA):
    """A test class for testing stacks of pushdown automata."""

    stack: PDAStack

    def setUp(self) -> None:
        self.stack = PDAStack(["a", "b"])

    def test_stack_hashability(self) -> None:
        self.assertEqual(hash(self.stack), hash(PDAStack(["a", "b"])))

    def test_stack_iter(self) -> None:
        """Should loop through the PDA stack in some manner."""
        self.assertEqual(list(self.stack), ["a", "b"])

    def test_stack_get(self) -> None:
        """Should retrieve indices in the PDA stack in some manner."""
        self.assertEqual(self.stack[0], "a")
        self.assertEqual(self.stack[1], "b")

    def test_stack_repr(self) -> None:
        """Should create proper string representation of PDA stack."""
        self.assertEqual(repr(self.stack), "PDAStack(('a', 'b'))")
