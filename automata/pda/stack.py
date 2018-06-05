#!/usr/bin/env python3
"""Classes and methods for working with PDA stacks."""

import collections


class PDAStack(collections.namedtuple('PDAStack', ['stack'])):
    """A PDA stack."""

    def __new__(cls, stack):
        """Create the new PDA stack."""
        if not isinstance(stack, tuple):
            stack = tuple(stack)
        return super(PDAStack, cls).__new__(cls, stack)

    def top(self):
        """Return the symbol at the top of the stack."""
        if self.stack:
            return self.stack[-1]
        else:
            return ''

    def pop(self):
        """
        Pop the stack top from the stack.

        Return a new PDAStack with the new content.
        """
        l = list(self.stack)
        l.pop()
        return self.__class__(l)

    def replace(self, symbols):
        """
        Replace the top of the stack with the given symbols.

        Return a new PDAStack with the new content.
        The first symbol in the given sequence becomes the new stack top.
        """
        l = list(self.stack)
        l.pop()
        l.extend(reversed(symbols))
        return self.__class__(l)

    def copy(self):
        """
        Return a deep copy of the stack.

        As this class is immutable, this has no effect.
        """
        return self

    def __len__(self):
        """Return the number of symbols on the stack."""
        return len(self.stack)

    def __iter__(self):
        """Return an interator for the stack."""
        return iter(self.stack)

    def __repr__(self):
        """Return a string representation of the stack."""
        return '{}({})'.format(self.__class__.__name__, self.stack)
