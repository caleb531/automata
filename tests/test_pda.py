#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAs."""

import nose.tools as nose

from automata.pda.pda import PDA, AcceptanceMode
from automata.pda.dpda import DPDA
from automata.pda.npda import NPDA


class TestPDA(object):
    """A test class for testing all pushdown automata."""

    def setup(self) -> None:
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
            acceptance_mode=AcceptanceMode.FINAL_STATE
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
            acceptance_mode=AcceptanceMode.FINAL_STATE
        )

    def assert_is_copy(self, first : 'PDA', second : 'PDA') -> None:
        """Assert that the first PDA is a deep copy of the second."""
        nose.assert_is_not(first.states, second.states)
        nose.assert_equal(first.states, second.states)
        nose.assert_is_not(first.input_symbols, second.input_symbols)
        nose.assert_equal(first.input_symbols, second.input_symbols)
        nose.assert_is_not(first.stack_symbols, second.stack_symbols)
        nose.assert_equal(first.stack_symbols, second.stack_symbols)
        nose.assert_is_not(first.transitions, second.transitions)
        nose.assert_equal(first.transitions, second.transitions)
        nose.assert_equal(first.initial_state, second.initial_state)
        nose.assert_equal(
            first.initial_stack_symbol, second.initial_stack_symbol)
        nose.assert_is_not(first.final_states, second.final_states)
        nose.assert_equal(first.final_states, second.final_states)
        nose.assert_equal(first.acceptance_mode, second.acceptance_mode)
