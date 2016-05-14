#!/usr/bin/env python3
"""Classes and methods for working with all pushdown automata."""

import abc

from automata.shared.automaton import Automaton


class PDA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for pushdown automata."""

    pass
