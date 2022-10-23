#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc

from frozendict import frozendict

import automata.base.exceptions as exceptions
from automata.base.utils import freezeValue


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            object.__setattr__(self, attr_name, freezeValue(attr_value))
        self.__post_init__()

    def __post_init__(self):
        self.validate()

    @abc.abstractmethod
    def validate(self):
        """Return True if this automaton is internally consistent."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_input_stepwise(self, input_str):
        """Return a generator that yields each step while reading input."""
        raise NotImplementedError

    def read_input(self, input_str):
        """
        Check if the given string is accepted by this automaton.

        Return the automaton's final configuration if this string is valid.
        """
        validation_generator = self.read_input_stepwise(input_str)
        # "Fast-forward" generator to get its final value
        for config in validation_generator:
            pass
        return config

    def accepts_input(self, input_str):
        """Return True if this automaton accepts the given input."""
        try:
            self.read_input(input_str)
            return True
        except exceptions.RejectionException:
            return False

    def _validate_initial_state(self):
        """Raise an error if the initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} is not a valid initial state'.format(self.initial_state))

    def _validate_initial_state_transitions(self):
        """Raise an error if the initial state has no transitions defined."""
        if self.initial_state not in self.transitions and len(self.states) > 1:
            raise exceptions.MissingStateError(
                'initial state {} has no transitions defined'.format(
                    self.initial_state))

    def _validate_final_states(self):
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'final states are not valid ({})'.format(
                    ', '.join(str(state) for state in invalid_states)))

    def copy(self):
        """Create a deep copy of the automaton."""
        return self.__class__(**vars(self))

    # Format the given value for string output via repr() or str(); this exists for the purpose of displaying
    def _get_value_repr(self, value):
        if isinstance(value, frozenset):
            return set(value)
        elif isinstance(value, frozendict):
            return {
                dict_key: self._get_value_repr(dict_value)
                for dict_key, dict_value in value.items()
            }
        else:
            return value

    def __repr__(self):
        values = ', '.join([
            f'{attr_name}={self._get_value_repr(attr_value)}'
            for attr_name, attr_value in self.__dict__.items()])
        return f'{self.__class__.__name__}({values})'
