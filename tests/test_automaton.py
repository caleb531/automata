#!/usr/bin/env python3
"""Functions for testing the Automaton abstract base class."""

import nose.tools as nose

from automata.base.automaton import Automaton


def test_abstract_methods_not_implemented():
    """Should raise NotImplementedError when calling abstract methods."""
    abstract_methods = {
        '__init__': (Automaton,),
        'validate': (Automaton,),
        'read_input_stepwise': (Automaton, '')
    }
    for method_name, method_args in abstract_methods.items():
        with nose.assert_raises(NotImplementedError):
            getattr(Automaton, method_name)(*method_args)
