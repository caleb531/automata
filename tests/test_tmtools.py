#!/usr/bin/env python3
"""Classes and functions for testing the Turing machine utility functions."""

import contextlib
import io
from unittest.mock import call, patch

import nose.tools as nose

import automata.tm.tools as tmtools
import tests.test_tm as test_tm
from automata.tm.configuration import TMConfiguration
from automata.tm.tape import TMTape


class TestTMTools(test_tm.TestTM):
    """A test class for testing Turing machine utility functions."""

    def test_print_config(self):
        """Should print the given configuration to stdout."""
        out = io.StringIO()
        config = TMConfiguration(
            'q2',
            TMTape(
                tape='abcdefghij',
                blank_symbol='.',
                current_position=2,
            )
        )
        with contextlib.redirect_stdout(out):
            config.print()
        nose.assert_equal(out.getvalue().rstrip(), '{}: {}\n{}'.format(
            'q2', 'abcdefghij', '^'.rjust(7)))

    @patch('automata.tm.configuration.TMConfiguration.print')
    def test_print_configs(self, print_config):
        """Should print each machine configuration to stdout."""
        tape1 = TMTape(
            tape='01010101',
            blank_symbol='.',
            current_position=0,
        )
        tape2 = TMTape(
            tape='x1010101',
            blank_symbol='.',
            current_position=-1,
        )
        tape3 = TMTape(
            tape='yx1010101',
            blank_symbol='.',
            current_position=-2,
        )
        configs = [
            TMConfiguration(tape1, 'q0'),
            TMConfiguration(tape2, 'q1'),
            TMConfiguration(tape3, 'q2')
        ]
        tmtools.print_configs(configs)
        nose.assert_equal(print_config.call_args_list, [
            call(),
            call(),
            call()
        ])

    def test_tape_iteration(self):
        """Should be able to iterate over a Turing machine tape."""
        tape = TMTape(
            tape='abcdef',
            blank_symbol='.',
            current_position=2,
        )
        nose.assert_equal(tuple(tape), ('a', 'b', 'c', 'd', 'e', 'f'))
