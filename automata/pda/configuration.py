#!/usr/bin/env python3
"""Classes and methods for working with PDA configurations."""


class PDAConfiguration(object):
    """
    A configuration is a triple of current state, remaining input and stack.

    It represents the complete runtime state of a PDA.
    """

    def __init__(self, state, remaining_input, stack):
        """Initialize the new PDA configuration."""
        self.state = state
        self.remaining_input = remaining_input
        self.stack = stack

    def replace_stack_top(self, new_stack_top):
        if new_stack_top == '':
            self.stack.pop()
        else:
            self.stack.replace(new_stack_top)

    def pop_symbol(self):
        symbol = self.remaining_input[0]
        self.remaining_input = self.remaining_input[1:]
        return symbol

    def copy(self):
        """Return a deep copy of the PDA configuration."""
        return self.__class__(
            self.state, self.remaining_input, self.stack.copy()
        )

    def __repr__(self):
        """Return a string representation of the configuration."""
        return '{}({})'.format(self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        """Check if two configurations are equal."""
        return self.__dict__ == other.__dict__
