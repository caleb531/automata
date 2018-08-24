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

    def print(self):
        """Print the machine's current configuration in a readable form."""
        print('{current_state}: {tape}\n{current_position}'.format(
            current_state=self.state,
            tape=''.join(self.tape).rjust(
                len(self.tape),
                self.tape.blank_symbol),
            current_position='^'.rjust(
                self.tape.current_position + len(self.state) + 3
            ),
        ))
