#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc

import automata.shared.exceptions as exceptions


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """Initialize a complete automaton."""
        pass

    @abc.abstractmethod
    def validate_self(self):
        """Return True if this automaton is internally consistent."""
        pass

    @abc.abstractmethod
    def validate_input(self, input_str):
        """Check if the given string is accepted by this automaton."""
        pass

    def _validate_initial_state(self):
        """Raise an error if an initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} is not a valid initial state'.format(self.initial_state))

    def _validate_final_states(self):
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'final states are not valid ({})'.format(
                    ', '.join(invalid_states)))

    def copy(self):
        """Create an exact copy of the automaton."""
        return self.__class__(self)

    def __eq__(self, other):
        """Check if two automata are equal."""
        return self.__dict__ == other.__dict__
