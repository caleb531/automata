#!/usr/bin/env python3
"""Classes and functions for testing the behavior of MNTMs."""

from automata.tm.mntm import MNTM

tm = MNTM(
    states={'q0', 'q1'},
    input_symbols={'0', '1'},
    tape_symbols={'0', '1', '#'},
    n_tapes=2,
    transitions={
        'q0': {
            ('1', '#'): [('q0', (('1', 'R'), ('1', 'R')))],
            ('0', '#'): [('q0', (('0', 'R'), ('#', 'N')))],
            ('#', '#'): [('q1', (('#', 'N'), ('#', 'N')))]
        }
    },
    initial_state='q0',
    blank_symbol='#',
    final_states={'q1'}
)

# for conf in tm.read_input_stepwise('10011110'):
#     print(conf)

for conf in tm.simulate_as_ntm('10011110'):
    print(conf)
