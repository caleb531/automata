#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
from typing import Any, Iterable

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

        if isinstance(state_data, (set, frozenset, list, tuple)):
            inner = ", ".join(FA.get_state_name(sub_data) for sub_data in state_data)
            if isinstance(state_data, (set, frozenset)):
                return "{" + inner + "}"

            if isinstance(state_data, tuple):
                return "(" + inner + ")"

            if isinstance(state_data, list):
                return "[" + inner + "]"

        return str(state_data)

    @abc.abstractmethod
    def iter_states(self) -> Iterable[Any]:
        """Iterate over all states in the automaton."""

    @abc.abstractmethod
    def iter_transitions(self) -> Iterable[tuple[Any, Any, Any]]:
        """
        Iterate over all transitions in the automaton. Each transition is a tuple
        of the form (from_state, to_state, symbol)
        """

    @abc.abstractmethod
    def is_accepted(self, state) -> bool:
        """Check if a state is an accepting state."""

    @abc.abstractmethod
    def is_initial(self, state) -> bool:
        """Check if a state is an initial state."""
