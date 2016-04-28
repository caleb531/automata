#!/usr/bin/env python3
"""Classes and functions for testing the Turing machine utility functions."""

import contextlib
import io

import nose.tools as nose

import turingmachines.tools as tmtools
import tests.test_tm as test_tm
from turingmachines.tape import TuringMachineTape


class TestTMTools(test_tm.TestTM):
    """A test class for testing Turing machine utility functions."""

    def test_print_config(self):
        """Should print the given configuration to stdout."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tmtools.print_config(
                current_state='q2', tape=TuringMachineTape(
                    tape='abcdefghij', blank_symbol='.',
                    current_position=2, position_offset=-2),
                min_position_offset=2)
        nose.assert_equal(out.getvalue().rstrip(), '{}: {}\n{}'.format(
            'q2', 'abcdefghij', '^'.rjust(5)))
