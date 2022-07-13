#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import unittest

import automata.base.exceptions as exceptions
from automata.tm.dtm import DTM
from automata.tm.ntm import NTM
from automata.tm.mntm import MNTM


class TestTM(unittest.TestCase):
    """A test class for testing all Turing machines."""

    def setUp(self):
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
        # NTM which accepts the following:
        # '2'.join(['<one or more zeroes>' + '1']*<one or more>)
        # + '<any amount of ones>'
        self.ntm1 = NTM(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1', '2'},
            tape_symbols={'0', '1', '2', '.'},
            transitions={
                'q0': {
                    '0': {('q0', '0', 'R')},
                    '1': {('q1', '1', 'R'), ('q2', '1', 'R')},
                },
                'q1': {
                    '1': {('q1', '1', 'R')},
                    '.': {('q3', '.', 'N')},
                },
                'q2': {
                    '2': {('q0', '2', 'R')},
                },
            },
            initial_state='q0',
            blank_symbol='.',
            final_states={'q3'}
        )
        # MNTM which accepts all strings in {0, 1}* and writes all
        # 1's from the first tape (input) to the second tape.
        self.mntm1 = MNTM(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', '#'},
            n_tapes=2,
            transitions={
                'q0': {
                    ('1', '#'): [('q0', (('1', 'R'), ('1', 'R')))],
                    ('0', '#'): [('q0', (('0', 'R'), ('#', 'N')))],
                    ('#', '#'): [('q1', (('#', 'N'), ('#', 'N')))],
                }
            },
            initial_state='q0',
            blank_symbol='#',
            final_states={'q1'},
        )
        # MNTM which accepts all strings with a number of 0's of the form
        # n^2, i.e is a square number. The string starts with '#'.
        self.mntm2 = MNTM(
            states=set(['q' + str(i)
                        for i in range(-1, 27)] + ['qc', 'qf', 'qr']),
            input_symbols={'0'},
            tape_symbols={'0', 'X', 'Y', 'S', '#'},
            n_tapes=3,
            transitions={
                'q-1': {
                    ('#', '#', '#'): [('q0', (('#', 'R'), ('#', 'N'),
                                              ('#', 'N')))]
                },
                'q0': {
                    ('0', '#', '#'): [('q1', (('0', 'N'), ('#', 'R'),
                                              ('#', 'R')))]
                },
                'q1': {
                    ('0', '#', '#'): [('q2', (('0', 'N'), ('0', 'R'),
                                              ('#', 'N')))]
                },
                'q2': {
                    ('0', '#', '#'): [('qc', (('0', 'N'), ('#', 'L'),
                                              ('X', 'R')))]
                },
                'qc': {
                    ('0', '0', '#'): [
                        ('qc', (('0', 'R'), ('0', 'R'), ('#', 'N')))
                    ],  # Testing whether tape 1 and 2 have the same length
                    ('0', '#', '#'): [
                        ('q3', (('0', 'N'), ('#', 'N'), ('#', 'N')))
                    ],  # length of tape 1 is greater than tape 2'N (continues)
                    ('#', '#', '#'): [
                        ('qf', (('#', 'N'), ('#', 'N'), ('#', 'N')))
                    ],  # tape 1 and 2 were found to be of equal length
                        # accepts
                    ('#', '0', '#'): [
                        ('qr', (('#', 'N'), ('0', 'N'), ('#', 'N')))
                    ],  # length of tape 2 is greater than tape 1'N (rejects)
                },
                'q3': {
                    ('0', '#', '#'): [('q4', (('0', 'N'), ('#', 'N'),
                                              ('#', 'L')))]
                },
                'q4': {
                    ('0', '#', 'X'): [('q5', (('0', 'N'), ('#', 'N'),
                                              ('X', 'R')))],
                    ('0', '#', 'Y'): [('q13', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                },
                'q5': {
                    ('0', '#', 'Y'): [('q5', (('0', 'N'), ('#', 'N'),
                                              ('Y', 'L')))],
                    ('0', '#', '#'): [('q6', (('0', 'N'), ('#', 'N'),
                                              ('Y', 'L')))],
                },
                'q6': {
                    ('0', '#', 'X'): [('q6', (('0', 'N'), ('#', 'N'),
                                              ('X', 'L')))],
                    ('0', '#', 'Y'): [('q7', (('0', 'N'), ('#', 'N'),
                                              ('Y', 'R')))],
                    ('0', '#', 'S'): [('q7', (('0', 'N'), ('#', 'N'),
                                              ('S', 'R')))],
                    ('0', '#', '#'): [
                        ('q24', (('0', 'N'), ('#', 'N'), ('#', 'R')))
                    ],
                },
                'q7': {
                    ('0', '#', 'X'): [('q9', (('0', 'N'), ('#', 'N'),
                                              ('S', 'R')))]
                },
                'q9': {
                    ('0', '#', 'X'): [('q9', (('0', 'N'), ('#', 'N'),
                                              ('X', 'R')))],
                    ('0', '#', 'Y'): [('q9', (('0', 'N'), ('#', 'N'),
                                              ('Y', 'R')))],
                    ('0', '#', '#'): [('q10', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                },
                'q10': {
                    ('0', '#', 'Y'): [('q10', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                    ('0', '#', 'X'): [('q6', (('0', 'N'), ('#', 'N'),
                                              ('X', 'L')))],
                    ('0', '#', 'S'): [('q11', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                },
                'q11': {
                    ('0', '#', 'S'): [('q11', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                    ('0', '#', 'Y'): [('q11', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                    ('0', '#', 'X'): [('q11', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                    ('0', '#', '#'): [('q12', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                },
                'q12': {
                    ('0', '#', 'X'): [('q20', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                    ('0', '#', 'Y'): [('q21', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                },
                'q13': {
                    ('0', '#', 'X'): [('q13', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                    ('0', '#', '#'): [('q14', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                },
                'q14': {
                    ('0', '#', 'Y'): [('q14', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                    ('0', '#', 'X'): [('q15', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                    ('0', '#', 'S'): [('q15', (('0', 'N'), ('#', 'N'),
                                               ('S', 'R')))],
                },
                'q15': {
                    ('0', '#', 'Y'): [('q17', (('0', 'N'), ('#', 'N'),
                                               ('S', 'R')))]
                },
                'q17': {
                    ('0', '#', 'Y'): [('q17', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                    ('0', '#', 'X'): [('q17', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                    ('0', '#', '#'): [('q18', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                },
                'q18': {
                    ('0', '#', 'X'): [('q18', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                    ('0', '#', 'Y'): [('q14', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                    ('0', '#', 'S'): [('q19', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                },
                'q19': {
                    ('0', '#', 'S'): [('q19', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                    ('0', '#', 'X'): [('q19', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                    ('0', '#', 'Y'): [('q19', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                    ('0', '#', '#'): [('q12', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                },
                'q20': {
                    ('0', '#', 'X'): [('q20', (('0', 'N'), ('#', 'N'),
                                               ('X', 'L')))],
                    ('0', '#', 'Y'): [('q22', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                },
                'q21': {
                    ('0', '#', 'Y'): [('q21', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))],
                    ('0', '#', 'X'): [('q22', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                },
                'q22': {
                    ('0', '#', 'X'): [('q22', (('0', 'N'), ('0', 'R'),
                                               ('X', 'R')))],
                    ('0', '#', 'Y'): [('q22', (('0', 'N'), ('0', 'R'),
                                               ('Y', 'R')))],
                    ('0', '#', '#'): [('q23', (('0', 'N'), ('#', 'N'),
                                               ('#', 'N')))],
                },
                'q23': {
                    ('0', '#', '#'): [('q23', (('0', 'L'), ('#', 'N'),
                                               ('#', 'N')))],
                    ('#', '#', '#'): [('q26', (('#', 'R'), ('#', 'L'),
                                               ('#', 'N')))],
                },
                'q26': {
                    ('0', '0', '#'): [('q26', (('0', 'N'), ('0', 'L'),
                                               ('#', 'N')))],
                    ('0', '#', '#'): [('qc', (('0', 'N'), ('#', 'R'),
                                              ('#', 'N')))],
                },
                'q24': {
                    ('0', '#', 'Y'): [('q24', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                    ('0', '#', 'X'): [('q24', (('0', 'N'), ('#', 'N'),
                                               ('X', 'R')))],
                    ('0', '#', '#'): [('q25', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'R')))],
                },
                'q25': {
                    ('0', '#', '#'): [('q12', (('0', 'N'), ('#', 'N'),
                                               ('Y', 'L')))]
                },
            },
            initial_state='q-1',
            blank_symbol='#',
            final_states={'qf'},
        )

        # MNTM which accepts all strings of the form ww, where w is in {0, 1}*
        self.mntm3 = MNTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', '$', '#'},
            n_tapes=3,
            transitions={
                'q0': {
                    ('0', '#', '#'): [('q1', (('0', 'N'), ('$', 'R'),
                                              ('$', 'R')))],
                    ('1', '#', '#'): [('q1', (('1', 'N'), ('$', 'R'),
                                              ('$', 'R')))]
                },
                'q1': {
                    ('0', '#', '#'): [('q1', (('0', 'R'), ('0', 'R'),
                                              ('#', 'N'))),
                                      ('q2', (('0', 'R'), ('#', 'N'),
                                              ('0', 'R')))],
                    ('1', '#', '#'): [('q1', (('1', 'R'), ('1', 'R'),
                                              ('#', 'N'))),
                                      ('q2', (('1', 'R'), ('#', 'N'),
                                              ('1', 'R')))],
                },
                'q2': {
                    ('0', '#', '#'): [('q2', (('0', 'R'), ('#', 'N'),
                                              ('0', 'R')))],
                    ('1', '#', '#'): [('q2', (('1', 'R'), ('#', 'N'),
                                              ('1', 'R')))],
                    ('#', '#', '#'): [('q3', (('#', 'N'), ('#', 'L'),
                                              ('#', 'L')))]
                },
                'q3': {
                    ('#', '0', '0'): [('q3', (('#', 'N'), ('0', 'L'),
                                              ('0', 'L')))],
                    ('#', '1', '1'): [('q3', (('#', 'N'), ('1', 'L'),
                                              ('1', 'L')))],
                    ('#', '$', '$'): [('q4', (('#', 'N'), ('$', 'N'),
                                              ('$', 'N')))]
                }
            },
            initial_state='q0',
            blank_symbol='#',
            final_states={'q4'},
        )

    def assert_is_copy(self, first, second):
        """Assert that the first FA is a deep copy of the second."""
        self.assertIsNot(first.states, second.states)
        self.assertEqual(first.states, second.states)
        self.assertIsNot(first.input_symbols, second.input_symbols)
        self.assertEqual(first.input_symbols, second.input_symbols)
        self.assertIsNot(first.tape_symbols, second.tape_symbols)
        self.assertEqual(first.tape_symbols, second.tape_symbols)
        self.assertIsNot(first.transitions, second.transitions)
        self.assertEqual(first.transitions, second.transitions)
        self.assertEqual(first.initial_state, second.initial_state)
        self.assertEqual(first.blank_symbol, second.blank_symbol)
        self.assertIsNot(first.final_states, second.final_states)
        self.assertEqual(first.final_states, second.final_states)

    def test_validate_blank_symbol(self):
        self.dtm1.blank_symbol = '-'
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.dtm1.validate()
