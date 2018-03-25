#!/usr/bin/env python3
"""Functions for testing the Automaton abstract base class."""

import nose.tools as nose

from automata.base.automaton import Automaton


def test_abstract_methods_not_implemented():
    """Should raise NotImplementedError when calling abstract methods."""
    with nose.assert_raises(NotImplementedError):
        Automaton.__init__(Automaton)
    with nose.assert_raises(NotImplementedError):
        Automaton._init_from_formal_params(Automaton)
    with nose.assert_raises(NotImplementedError):
        Automaton.validate_self(Automaton)
    with nose.assert_raises(NotImplementedError):
        Automaton._validate_input_yield(Automaton, None)
