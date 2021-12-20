#!/usr/bin/env python3
"""Classes and methods for working with PDA stacks."""

import collections
from typing import Iterator, Reversible

class PDAStack(collections.namedtuple('PDAStack', ['stack'])):
    """A PDA stack."""

    def __new__(cls, *elements) -> 'PDAStack':
        """Create the new PDA stack."""
        if len(elements) == 1:
            stack = tuple(elements[0])
        else:
            stack = elements
        return super(PDAStack, cls).__new__(cls, stack)

    def top(self) -> str:
        """Return the symbol at the top of the stack."""
        if self.stack:
            return self.stack[-1]
        else:
            return ''

    def pop(self) -> 'PDAStack':
        """
        Pop the stack top from the stack.

        Return a new PDAStack with the new content.
        """
        stack_contents = list(self.stack)
        stack_contents.pop()
        return self.__class__(stack_contents)

    def replace(self, symbols : Reversible[str]) -> 'PDAStack':
        """
        Replace the top of the stack with the given symbols.

        Return a new PDAStack with the new content.
        The first symbol in the given sequence becomes the new stack top.
        """
        stack_contents = list(self.stack)
        stack_contents.pop()
        stack_contents.extend(reversed(symbols))
        return self.__class__(stack_contents)

    def __len__(self) -> int:
        """Return the number of symbols on the stack."""
        return len(self.stack)

    def __iter__(self) -> Iterator[str]:
        """Return an interator for the stack."""
        return iter(self.stack)

    def __repr__(self) -> str:
        """Return a string representation of the stack."""
        return '{}{}'.format(self.__class__.__name__, self.stack)
