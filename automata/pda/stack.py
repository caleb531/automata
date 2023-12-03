#!/usr/bin/env python3
"""Classes and methods for working with PDA stacks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Sequence, Tuple


@dataclass(frozen=True)
class PDAStack:
    """A PDA stack."""

    __slots__ = ("stack",)

    stack: Tuple[str, ...]

    def __init__(self, stack: Sequence[str]) -> None:
        object.__setattr__(self, "stack", tuple(stack))

    def top(self) -> str:
        """
        Return the symbol at the top of the stack.

        Returns
        ----------
        str
            The symbol at the top of the stack. Returns the empty
            string if the stack is empty.
        """
        if self.stack:
            return self.stack[-1]

        return ""

    def pop(self) -> PDAStack:
        """
        Pop the top element from the stack and return
        the new stack.

        Returns
        ----------
        PDAStack
            A copy of the old PDAStack with the top element removed.
        """
        return self.__class__(self.stack[:-1])

    def replace(self, symbols: Sequence[str]) -> PDAStack:
        """
        Replace the top of the stack with the given symbols.

        Parameters
        ----------
        symbols : Sequence[str]
            A sequence of symbols to add to the top of the PDAStack.
            The first symbol in the given sequence becomes the new stack top.

        Returns
        ----------
        PDAStack
            A copy of the old PDAStack with the top element replaced.
        """
        return self.__class__(self.stack[:-1] + tuple(reversed(symbols)))

    def __len__(self) -> int:
        """Return the number of symbols on the stack."""
        return len(self.stack)

    def __iter__(self) -> Iterator[str]:
        """Return an iterator for the stack."""
        return iter(self.stack)

    def __getitem__(self, key: int | slice) -> str | Sequence[str]:
        """Return the stack element at the given index"""
        return self.stack[key]

    def __reversed__(self) -> Iterator[str]:
        """Return an iterator for the stack in reversed order"""
        return reversed(self.stack)

    def __repr__(self) -> str:
        """Return a string representation of the stack."""
        return "{}({})".format(self.__class__.__name__, self.stack)

    def __eq__(self, other: Any) -> bool:
        """Return True if two PDAConfiguration are equivalent"""
        if not isinstance(other, PDAStack):
            return NotImplemented

        return self.stack == other.stack
