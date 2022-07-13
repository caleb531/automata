#!/usr/bin/env python3
"""Functions for testing the Automaton abstract base class."""

import unittest

from automata.base.automaton import Automaton


class TestAutomaton(unittest.TestCase):

    def test_abstract_methods_not_implemented(self):
        """Should raise NotImplementedError when calling abstract methods."""
        abstract_methods = {
            '__init__': (Automaton,),
            'validate': (Automaton,),
            'read_input_stepwise': (Automaton, '')
        }
        for method_name, method_args in abstract_methods.items():
            with self.assertRaises(NotImplementedError):
                getattr(Automaton, method_name)(*method_args)
