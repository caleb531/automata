#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAs."""

import unittest

from automata.pda.dpda import DPDA
from automata.pda.npda import NPDA


class TestPDA(unittest.TestCase):
    """A test class for testing all pushdown automata."""

    def setUp(self):
        """Reset test automata before every test function."""
        # DPDA which which matches zero or more 'a's, followed by the same
        # number of 'b's (accepting by final state)
        self.dpda = DPDA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a', 'b'},
            stack_symbols={'0', '1'},
            transitions={
                'q0': {
                    'a': {'0': ('q1', ('1', '0'))}
                },
                'q1': {
                    'a': {'1': ('q1', ('1', '1'))},
                    'b': {'1': ('q2', '')}
                },
                'q2': {
                    'b': {'1': ('q2', '')},
                    '': {'0': ('q3', ('0',))}
                }
            },
            initial_state='q0',
            initial_stack_symbol='0',
            final_states={'q3'},
            acceptance_mode='final_state'
        )

        # NPDA which matches palindromes consisting of 'a's and 'b's
        # (accepting by final state)
        # q0 reads the first half of the word, q1 the other half, q2 accepts.
        # But we have to guess when to switch.
        self.npda = NPDA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            stack_symbols={'A', 'B', '#'},
            transitions={
                'q0': {
                    '': {
                        '#': {('q2', '#')},
                    },
                    'a': {
                        '#': {('q0', ('A', '#'))},
                        'A': {
                            ('q0', ('A', 'A')),
                            ('q1', ''),
                        },
                        'B': {('q0', ('A', 'B'))},
                    },
                    'b': {
                        '#': {('q0', ('B', '#'))},
                        'A': {('q0', ('B', 'A'))},
                        'B': {
                            ('q0', ('B', 'B')),
                            ('q1', ''),
                        },
                    },
                },
                'q1': {
                    '': {'#': {('q2', '#')}},
                    'a': {'A': {('q1', '')}},
                    'b': {'B': {('q1', '')}},
                }
            },
            initial_state='q0',
            initial_stack_symbol='#',
            final_states={'q2'},
            acceptance_mode='final_state'
        )
