#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
from typing import Collection, Iterable, Mapping, Set

from automata.base.automaton import Automaton, AutomatonStateT

FAStateT = AutomatonStateT


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    __slots__ = tuple()

    @staticmethod
    def get_state_name(state_data):
        """
        Get an string representation of a state. This is used for displaying and
        uses `str` for any unsupported python data types.
        """
        if isinstance(state_data, str):
            if state_data == "":
                return "λ"

            return state_data

        if isinstance(state_data, (Set, list, tuple)):
            inner = ", ".join(FA.get_state_name(sub_data) for sub_data in state_data)
            if isinstance(state_data, Set):
                return "{" + inner + "}"

            if isinstance(state_data, tuple):
                return "(" + inner + ")"

            if isinstance(state_data, list):
                return "[" + inner + "]"

        return str(state_data)
