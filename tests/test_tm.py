#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DTMs."""

import nose.tools as nose

import automata.base.exceptions as exceptions
from automata.tm.tape import HeadDirection
from automata.tm.tm import TM
from automata.tm.dtm import DTM
from automata.tm.ntm import NTM
from automata.tm.mntm import MNTM


class TestTM(object):
    """A test class for testing all Turing machines."""

    def setup(self) -> None:
        """Reset test machines before every test function."""
        # DTM which matches all strings beginning with '0's, and followed by
        # the same number of '1's
        self.dtm1 = DTM(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            tape_symbols={'0', '1', 'x', 'y', '.'},
            transitions={
                'q0': {
                    '0': ('q1', 'x', HeadDirection.R),
                    'y': ('q3', 'y', HeadDirection.R)
                },
                'q1': {
                    '0': ('q1', '0', HeadDirection.R),
                    '1': ('q2', 'y', HeadDirection.L),
                    'y': ('q1', 'y', HeadDirection.R)
                },
                'q2': {
                    '0': ('q2', '0', HeadDirection.L),
                    'x': ('q0', 'x', HeadDirection.R),
                    'y': ('q2', 'y', HeadDirection.L)
                },
                'q3': {
                    'y': ('q3', 'y', HeadDirection.R),
                    '.': ('q4', '.', HeadDirection.R)
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
                    '0': ('q1', 'x', HeadDirection.L)
                },
                'q1': {
                    '.': ('q2', 'y', HeadDirection.L)
                },
                'q2': {
                    '.': ('q3', 'y', HeadDirection.R)
                },
                'q3': {
                    'y': ('q3', 'y', HeadDirection.R),
                    'x': ('q4', 'x', HeadDirection.R)
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
                    '0': {('q0', '0', HeadDirection.R)},
                    '1': {('q1', '1', HeadDirection.R), ('q2', '1', HeadDirection.R)},
                },
                'q1': {
                    '1': {('q1', '1', HeadDirection.R)},
                    '.': {('q3', '.', HeadDirection.N)},
                },
                'q2': {
                    '2': {('q0', '2', HeadDirection.R)},
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
                    ('1', '#'): [('q0', (('1', HeadDirection.R), ('1', HeadDirection.R)))],
                    ('0', '#'): [('q0', (('0', HeadDirection.R), ('#', HeadDirection.N)))],
                    ('#', '#'): [('q1', (('#', HeadDirection.N), ('#', HeadDirection.N)))],
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
                    ('#', '#', '#'): [('q0', (('#', HeadDirection.R), ('#', HeadDirection.N),
                                              ('#', HeadDirection.N)))]
                },
                'q0': {
                    ('0', '#', '#'): [('q1', (('0', HeadDirection.N), ('#', HeadDirection.R),
                                              ('#', HeadDirection.R)))]
                },
                'q1': {
                    ('0', '#', '#'): [('q2', (('0', HeadDirection.N), ('0', HeadDirection.R),
                                              ('#', HeadDirection.N)))]
                },
                'q2': {
                    ('0', '#', '#'): [('qc', (('0', HeadDirection.N), ('#', HeadDirection.L),
                                              ('X', HeadDirection.R)))]
                },
                'qc': {
                    ('0', '0', '#'): [
                        ('qc', (('0', HeadDirection.R), ('0', HeadDirection.R), ('#', HeadDirection.N)))
                    ],  # Testing whether tape 1 and 2 have the same length
                    ('0', '#', '#'): [
                        ('q3', (('0', HeadDirection.N), ('#', HeadDirection.N), ('#', HeadDirection.N)))
                    ],  # length of tape 1 is greater than tape 2'N (continues)
                    ('#', '#', '#'): [
                        ('qf', (('#', HeadDirection.N), ('#', HeadDirection.N), ('#', HeadDirection.N)))
                    ],  # tape 1 and 2 were found to be of equal length
                        # accepts
                    ('#', '0', '#'): [
                        ('qr', (('#', HeadDirection.N), ('0', HeadDirection.N), ('#', HeadDirection.N)))
                    ],  # length of tape 2 is greater than tape 1'N (rejects)
                },
                'q3': {
                    ('0', '#', '#'): [('q4', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('#', HeadDirection.L)))]
                },
                'q4': {
                    ('0', '#', 'X'): [('q5', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('X', HeadDirection.R)))],
                    ('0', '#', 'Y'): [('q13', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                },
                'q5': {
                    ('0', '#', 'Y'): [('q5', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('Y', HeadDirection.L)))],
                    ('0', '#', '#'): [('q6', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('Y', HeadDirection.L)))],
                },
                'q6': {
                    ('0', '#', 'X'): [('q6', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('X', HeadDirection.L)))],
                    ('0', '#', 'Y'): [('q7', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('Y', HeadDirection.R)))],
                    ('0', '#', 'S'): [('q7', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('S', HeadDirection.R)))],
                    ('0', '#', '#'): [
                        ('q24', (('0', HeadDirection.N), ('#', HeadDirection.N), ('#', HeadDirection.R)))
                    ],
                },
                'q7': {
                    ('0', '#', 'X'): [('q9', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('S', HeadDirection.R)))]
                },
                'q9': {
                    ('0', '#', 'X'): [('q9', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('X', HeadDirection.R)))],
                    ('0', '#', 'Y'): [('q9', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('Y', HeadDirection.R)))],
                    ('0', '#', '#'): [('q10', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                },
                'q10': {
                    ('0', '#', 'Y'): [('q10', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                    ('0', '#', 'X'): [('q6', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                              ('X', HeadDirection.L)))],
                    ('0', '#', 'S'): [('q11', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                },
                'q11': {
                    ('0', '#', 'S'): [('q11', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                    ('0', '#', 'Y'): [('q11', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                    ('0', '#', 'X'): [('q11', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', '#'): [('q12', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                },
                'q12': {
                    ('0', '#', 'X'): [('q20', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                    ('0', '#', 'Y'): [('q21', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                },
                'q13': {
                    ('0', '#', 'X'): [('q13', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                    ('0', '#', '#'): [('q14', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                },
                'q14': {
                    ('0', '#', 'Y'): [('q14', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                    ('0', '#', 'X'): [('q15', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', 'S'): [('q15', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('S', HeadDirection.R)))],
                },
                'q15': {
                    ('0', '#', 'Y'): [('q17', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('S', HeadDirection.R)))]
                },
                'q17': {
                    ('0', '#', 'Y'): [('q17', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                    ('0', '#', 'X'): [('q17', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', '#'): [('q18', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                },
                'q18': {
                    ('0', '#', 'X'): [('q18', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                    ('0', '#', 'Y'): [('q14', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                    ('0', '#', 'S'): [('q19', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                },
                'q19': {
                    ('0', '#', 'S'): [('q19', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                    ('0', '#', 'X'): [('q19', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', 'Y'): [('q19', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                    ('0', '#', '#'): [('q12', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                },
                'q20': {
                    ('0', '#', 'X'): [('q20', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.L)))],
                    ('0', '#', 'Y'): [('q22', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                },
                'q21': {
                    ('0', '#', 'Y'): [('q21', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))],
                    ('0', '#', 'X'): [('q22', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                },
                'q22': {
                    ('0', '#', 'X'): [('q22', (('0', HeadDirection.N), ('0', HeadDirection.R),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', 'Y'): [('q22', (('0', HeadDirection.N), ('0', HeadDirection.R),
                                               ('Y', HeadDirection.R)))],
                    ('0', '#', '#'): [('q23', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('#', HeadDirection.N)))],
                },
                'q23': {
                    ('0', '#', '#'): [('q23', (('0', HeadDirection.L), ('#', HeadDirection.N),
                                               ('#', HeadDirection.N)))],
                    ('#', '#', '#'): [('q26', (('#', HeadDirection.R), ('#', HeadDirection.L),
                                               ('#', HeadDirection.N)))],
                },
                'q26': {
                    ('0', '0', '#'): [('q26', (('0', HeadDirection.N), ('0', HeadDirection.L),
                                               ('#', HeadDirection.N)))],
                    ('0', '#', '#'): [('qc', (('0', HeadDirection.N), ('#', HeadDirection.R),
                                              ('#', HeadDirection.N)))],
                },
                'q24': {
                    ('0', '#', 'Y'): [('q24', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                    ('0', '#', 'X'): [('q24', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('X', HeadDirection.R)))],
                    ('0', '#', '#'): [('q25', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.R)))],
                },
                'q25': {
                    ('0', '#', '#'): [('q12', (('0', HeadDirection.N), ('#', HeadDirection.N),
                                               ('Y', HeadDirection.L)))]
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
                    ('0', '#', '#'): [('q1', (('0', HeadDirection.N), ('$', HeadDirection.R),
                                              ('$', HeadDirection.R)))],
                    ('1', '#', '#'): [('q1', (('1', HeadDirection.N), ('$', HeadDirection.R),
                                              ('$', HeadDirection.R)))]
                },
                'q1': {
                    ('0', '#', '#'): [('q1', (('0', HeadDirection.R), ('0', HeadDirection.R),
                                              ('#', HeadDirection.N))),
                                      ('q2', (('0', HeadDirection.R), ('#', HeadDirection.N),
                                              ('0', HeadDirection.R)))],
                    ('1', '#', '#'): [('q1', (('1', HeadDirection.R), ('1', HeadDirection.R),
                                              ('#', HeadDirection.N))),
                                      ('q2', (('1', HeadDirection.R), ('#', HeadDirection.N),
                                              ('1', HeadDirection.R)))],
                },
                'q2': {
                    ('0', '#', '#'): [('q2', (('0', HeadDirection.R), ('#', HeadDirection.N),
                                              ('0', HeadDirection.R)))],
                    ('1', '#', '#'): [('q2', (('1', HeadDirection.R), ('#', HeadDirection.N),
                                              ('1', HeadDirection.R)))],
                    ('#', '#', '#'): [('q3', (('#', HeadDirection.N), ('#', HeadDirection.L),
                                              ('#', HeadDirection.L)))]
                },
                'q3': {
                    ('#', '0', '0'): [('q3', (('#', HeadDirection.N), ('0', HeadDirection.L),
                                              ('0', HeadDirection.L)))],
                    ('#', '1', '1'): [('q3', (('#', HeadDirection.N), ('1', HeadDirection.L),
                                              ('1', HeadDirection.L)))],
                    ('#', '$', '$'): [('q4', (('#', HeadDirection.N), ('$', HeadDirection.N),
                                              ('$', HeadDirection.N)))]
                }
            },
            initial_state='q0',
            blank_symbol='#',
            final_states={'q4'},
        )

    def assert_is_copy(self, first : 'TM', second : 'TM') -> None:
        """Assert that the first TM is a deep copy of the second."""
        nose.assert_is_not(first.states, second.states)
        nose.assert_equal(first.states, second.states)
        nose.assert_is_not(first.input_symbols, second.input_symbols)
        nose.assert_equal(first.input_symbols, second.input_symbols)
        nose.assert_is_not(first.tape_symbols, second.tape_symbols)
        nose.assert_equal(first.tape_symbols, second.tape_symbols)
        nose.assert_is_not(first.transitions, second.transitions)
        nose.assert_equal(first.transitions, second.transitions)
        nose.assert_equal(first.initial_state, second.initial_state)
        nose.assert_equal(first.blank_symbol, second.blank_symbol)
        nose.assert_is_not(first.final_states, second.final_states)
        nose.assert_equal(first.final_states, second.final_states)

    def test_validate_blank_symbol(self) -> None:
        self.dtm1.blank_symbol = '-'
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dtm1.validate()
