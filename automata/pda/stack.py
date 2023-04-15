#!/usr/bin/env python3
"""Classes and methods for working with PDA stacks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence, Tuple


@dataclass(frozen=True)
class PDAStack:
    """A PDA stack."""

    __slots__ = ("stack",)

    stack: Tuple[str, ...]

    def __init__(self, stack: Sequence[str]) -> None:
        object.__setattr__(self, "stack", tuple(stack))

    def top(self) -> str:
        """Return the symbol at the top of the stack."""
        if self.stack:
            return self.stack[-1]
        else:
            return ""

    def pop(self) -> PDAStack:
        """
        Pop the stack top from the stack.

        Return a new PDAStack with the new content.
        """
        return self.__class__(self.stack[:-1])

    def replace(self, symbols: Sequence[str]) -> PDAStack:
        """
        Replace the top of the stack with the given symbols.

        Return a new PDAStack with the new content.
        The first symbol in the given sequence becomes the new stack top.
        """
        return self.__class__(self.stack[:-1] + tuple(reversed(symbols)))

    def __len__(self) -> int:
        """Return the number of symbols on the stack."""
        return len(self.stack)

    def __iter__(self) -> Iterator[str]:
        """Return an interator for the stack."""
        return iter(self.stack)

    def __repr__(self) -> str:
        """Return a string representation of the stack."""
        return "{}({})".format(self.__class__.__name__, self.stack)
