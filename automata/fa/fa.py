#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc

from automata.base.automaton import Automaton


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    @staticmethod
    def _get_state_maps(state_set_a, state_set_b):
        """
        Generate state map dicts from given sets. Useful when the state set has
        to be a union of the state sets of component FAs.
        """

        state_map_a: Dict[FAStateT, int] = {
            state: i
            for i, state in enumerate(state_set_a)
        }

        state_map_b: Dict[FAStateT, int] = {
            state: i + len(state_map_a)
            for i, state in enumerate(state_set_b)
        }

        return (state_map_a, state_map_b)
