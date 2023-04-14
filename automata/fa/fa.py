#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
from typing import Iterable

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

        if isinstance(state_data, Iterable):
            try:
                state_items = sorted(state_data)
            except TypeError:
                state_items = state_data

            inner = ", ".join(FA.get_state_name(sub_data) for sub_data in state_items)
            if isinstance(state_data, (set, frozenset)):
                return "{" + inner + "}"

            if isinstance(state_data, tuple):
                return "(" + inner + ")"

            return "[" + inner + "]"

        return str(state_data)
