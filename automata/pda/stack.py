#!/usr/bin/env python3
"""Classes and methods for working with PDA stacks."""


class PDAStack(object):
    """A PDA stack."""

    def __init__(self, stack, **kwargs):
        """Initialize the new PDA stack."""
        if isinstance(stack, PDAStack):
            self._init_from_stack_obj(stack)
        else:
            self.stack = list(stack)

    def _init_from_stack_obj(self, stack_obj):
        """Initialize this Stack as a deep copy of the given Stack."""
        self.__init__(stack_obj.stack)

    def top(self):
        """Return the symbol at the top of the stack."""
        if self.stack:
            return self.stack[-1]
        else:
            return ''

    def pop(self):
        """Pop the stack top from the stack."""
        self.stack.pop()

    def replace(self, symbols):
        """
        Replace the top of the stack with the given symbols.

        The first symbol in the given sequence becomes the new stack top.
        """
        self.stack.pop()
        self.stack.extend(reversed(symbols))

    def copy(self):
        """Return a deep copy of the stack."""
        return self.__class__(self)

    def __len__(self):
        """Return the number of symbols on the stack."""
        return len(self.stack)

    def __iter__(self):
        """Return an interator for the stack."""
        return iter(self.stack)

    def __repr__(self):
        """Return a string representation of the stack."""
        return '{}({})'.format(self.__class__.__name__, self.stack)

    def __eq__(self, other):
        """Check if two stacks are equal."""
        return self.__dict__ == other.__dict__
