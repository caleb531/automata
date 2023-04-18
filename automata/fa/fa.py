#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
from typing import Set

from automata.base.automaton import Automaton, AutomatonStateT

FAStateT = AutomatonStateT


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    __slots__ = tuple()

    @staticmethod
    def _add_new_state(state_set: Set[FAStateT], start: int = 0) -> int:
        """Adds new state to the state set and returns it"""
        new_state = start
        while new_state in state_set:
            new_state += 1

        state_set.add(new_state)

        return new_state
