#!/usr/bin/env python3
"""Classes and functions for testing the Turing machine utility functions."""

import contextlib
import io
from unittest.mock import call, patch

import nose.tools as nose

import turingmachines.tools as tmtools
import tests.test_tm as test_tm
from turingmachines.tape import TMTape


class TestTMTools(test_tm.TestTM):
    """A test class for testing Turing machine utility functions."""

    def test_print_config(self):
        """Should print the given configuration to stdout."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tmtools.print_config(
                current_state='q2', tape=TMTape(
                    tape='abcdefghij', blank_symbol='.',
                    current_position=2, position_offset=1),
                max_position_offset=3)
        nose.assert_equal(out.getvalue().rstrip(), '{}: {}\n{}'.format(
            'q2', '..abcdefghij', '^'.rjust(10)))

    @patch('turingmachines.tools.print_config')
    def test_print_configs(self, print_config):
        """Should print each machine configuration to stdout."""
        tape1 = TMTape(
            tape='01010101',
            current_position=0,
            position_offset=0
        )
        tape2 = TMTape(
            tape='x1010101',
            current_position=-1,
            position_offset=0
        )
        tape3 = TMTape(
            tape='yx1010101',
            current_position=-2,
            position_offset=1
        )
        tmtools.print_configs([
            ('q0', tape1),
            ('q1', tape2),
            ('q2', tape3)
        ])
        nose.assert_equal(print_config.call_args_list, [
            call('q0', tape1, 1),
            call('q1', tape2, 1),
            call('q2', tape3, 1)
        ])

    def test_tape_iteration(self):
        """Should be able to iterate over a Turing machine tape."""
        tape = TMTape(
            tape='abcdef',
            current_position=2,
            position_offset=1
        )
        nose.assert_equal(tuple(tape), ('a', 'b', 'c', 'd', 'e', 'f'))
