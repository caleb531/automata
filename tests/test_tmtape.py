#!/usr/bin/env python3
"""Classes and functions for testing the behavior of TMTapes."""

import unittest

from automata.tm.tape import TMTape


class TestTMTape(unittest.TestCase):
    """A test class for testing all Turing machines."""

    def test_tape_copy(self):
        """Should copy TMTape."""
        tape = TMTape('0011', blank_symbol='#', current_position=0)
        new_tape = tape.copy()
        self.assertIsNot(new_tape, tape)
