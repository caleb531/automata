#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

from turingmachines.dtm import DTM


class TestTM(object):
    """A test class for testing all Turing machines."""

    def setup(self):
        """Reset test machines before every test function."""
        # DTM which matches all strings beginning with '0's, and followed by
        # the same number of '1's
        self.dtm1 = DTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', 'x', 'y', '.'},
            transitions={
                'q0': {
                    '0': ('q1', 'x', 'R'),
                    'y': ('q3', 'y', 'R')
                },
                'q1': {
                    '0': ('q1', '0', 'R'),
                    '1': ('q2', 'y', 'L'),
                    'y': ('q1', 'y', 'R')
                },
                'q2': {
                    '0': ('q2', '0', 'L'),
                    'x': ('q0', 'x', 'R'),
                    'y': ('q2', 'y', 'L')
                },
                'q3': {
                    'y': ('q3', 'y', 'R'),
                    '.': ('q4', '.', 'R')
                }
            },
            initial_state='q0',
            blank_symbol='.',
            final_states={'q4'}
        )
        # DTM which matches any binary string, but is designed to test the
        # tape's position offsetting algorithm
        self.dtm2 = DTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', 'x', 'y', '.'},
            transitions={
                'q0': {
                    '0': ('q1', 'x', 'L')
                },
                'q1': {
                    '.': ('q2', 'y', 'L')
                },
                'q2': {
                    '.': ('q3', 'y', 'R')
                },
                'q3': {
                    'y': ('q3', 'y', 'R'),
                    'x': ('q4', 'x', 'R')
                }
            },
            initial_state='q0',
            blank_symbol='.',
            final_states={'q4'}
        )
