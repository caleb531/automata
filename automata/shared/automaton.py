#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc

import automata.shared.exceptions as exceptions


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    @abc.abstractmethod
    def __init__(self, obj=None, **kwargs):
        """Initialize a complete automaton."""
        pass

    @abc.abstractmethod
    def validate_self(self):
        """Return True if this automaton is internally consistent."""
        pass

    @abc.abstractmethod
    def _validate_input_yield(self, input_str):
        """Check if the given string is accepted by this automaton."""
        pass

    def _validate_input_return(self, input_str):
        """
        Check if the given string is accepted by this automaton.

        Return the automaton's final configuration if this string is valid.
        """
        validation_generator = self._validate_input_yield(input_str)
        for config in validation_generator:
            pass
        return config

    def validate_input(self, input_str, step=False):
        """
        Check if the given string is accepted by this automaton.

        If step is True, yield the configuration at each step. Otherwise,
        return the final configuration.
        """
        if step:
            return self._validate_input_yield(input_str)
        else:
            return self._validate_input_return(input_str)

    def _validate_initial_state(self):
        """Raise an error if the initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} is not a valid initial state'.format(self.initial_state))

    def _validate_initial_state_transitions(self):
        """Raise an error if the initial state has no transitions defined."""
        if self.initial_state not in self.transitions:
            raise exceptions.MissingStateError(
                'initial state {} has no transitions defined'.format(
                    self.initial_state))

    def _validate_final_states(self):
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'final states are not valid ({})'.format(
                    ', '.join(invalid_states)))

    def copy(self):
        """Create a deep copy of the automaton."""
        return self.__class__(self)

    def __eq__(self, other):
        """Check if two automata are equal."""
        return self.__dict__ == other.__dict__
