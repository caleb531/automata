#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc

import automata.shared.exceptions as exceptions
from automata.shared.automaton import Automaton


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    def _validate_transition_start_states(self):
        """Raise an error if transition start states are missing."""
        missing_states = self.states - set(self.transitions.keys())
        if missing_states:
            raise exceptions.MissingStateError(
                'transition start states are missing ({})'.format(
                    ', '.join(missing_states)))

    def _validate_transition_end_states(self, path_states):
        """Raise an error if transition end states are invalid."""
        invalid_states = path_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'transition end states are not valid ({})'.format(
                    ', '.join(invalid_states)))
