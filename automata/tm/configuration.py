#!/usr/bin/env python3
"""Classes and methods for working with Turing machine configurations."""

import collections


class TMConfiguration(collections.namedtuple(
    'TMConfiguration',
    ['state', 'tape']
)):
    """A Turing machine configuration."""

    def __repr__(self):
        """Return a string representation of the configuration."""
        return '{}(\'{}\', \'{}\')'.format(
            self.__class__.__name__, self.state, self.tape
        )
