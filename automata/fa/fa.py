#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc

from automata.base.automaton import Automaton, AutomatonStateT

FAStateT = AutomatonStateT


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    pass
