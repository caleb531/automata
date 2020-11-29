#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

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
# tm = MNTM(
#     states={'q0', 'q1'},
#     input_symbols={'0', '1'},
#     tape_symbols={'0', '1', '#'},
#     n_tapes=1,
#     transitions={
#         'q0': {
#             ('0',): [('q0', (('1', 'R'),))],
#             ('1',): [('q0', (('0', 'R'),))],
#             ('#',): [('q1', (('#', 'N'),))]
#         }
#     },
#     initial_state='q0',
#     blank_symbol='#',
#     final_states={'q1'}
# )

i = 0
for conf in tm.read_input_stepwise('11011101'):
    pass

# print(tm.accepts_input('11011101'))
"""
'q0': {
            ('0', '#', '#'): {('q1', (('0', 'S', '$'), ('R', '$', 'R')))},
            ('1', '#', '#'): {('q1', (('1', 'S', '$'), ('R', '$', 'R')))}
        },
        'q1': {
            ('0', '#', '#'): {('q1', (('0', 'R', '0'), ('R', '#', 'S')))},
            ('1', '#', '#'): {('q1', (('1', 'R', '1'), ('R', '#', 'S')))}
"""
