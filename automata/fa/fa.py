#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc

from frozendict import frozendict

from automata.base.automaton import Automaton


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    def __setattr__(self, name, value):
        """Set custom setattr to make class immutable."""
        raise AttributeError(f'This {type(self).__name__} is immutable')

    def __delattr__(self, name):
        """Set custom delattr to make class immutable."""
        raise AttributeError(f'This {type(self).__name__} is immutable')

    def __hash__(self):
        return hash(frozendict(self.__dict__))
