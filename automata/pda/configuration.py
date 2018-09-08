#!/usr/bin/env python3
"""Classes and methods for working with PDA configurations."""

import collections


class PDAConfiguration(collections.namedtuple(
    'PDAConfiguration',
    ['state', 'remaining_input', 'stack']
)):
    """
    A configuration is a triple of current state, remaining input and stack.

    It represents the complete runtime state of a PDA.
    It is hashable and immutable.
    """

    def __repr__(self):
        """Return a string representation of the configuration."""
        return '{}(\'{}\', \'{}\', {})'.format(
            self.__class__.__name__,
            self.state,
            self.remaining_input,
            self.stack
        )
