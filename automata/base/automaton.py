#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc

import automata.base.exceptions as exceptions
from typing import Hashable, NoReturn, Generator

StateT = Hashable


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    @abc.abstractmethod
    def __init__(self) -> None:
        """Initialize a complete automaton."""
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self) -> bool:
        """Return True if this automaton is internally consistent."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_input_stepwise(self, input_str : str) -> Generator:
        """Return a generator that yields each step while reading input."""
        raise NotImplementedError

    def read_input(self, input_str : str) -> StateT:
        """
        Check if the given string is accepted by this automaton.

        Return the automaton's final configuration if this string is valid.
        """
        validation_generator = self.read_input_stepwise(input_str)
        for config in validation_generator:
            pass
        return config

    def accepts_input(self, input_str : str) -> bool:
        """Return True if this automaton accepts the given input."""
        try:
            self.read_input(input_str)
            return True
        except exceptions.RejectionException:
            return False

    def _validate_initial_state(self) -> None:
        """Raise an error if the initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} is not a valid initial state'.format(self.initial_state))

    def _validate_initial_state_transitions(self) -> None:
        """Raise an error if the initial state has no transitions defined."""
        if self.initial_state not in self.transitions:
            raise exceptions.MissingStateError(
                'initial state {} has no transitions defined'.format(
                    self.initial_state))

    def _validate_final_states(self) -> None:
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'final states are not valid ({})'.format(
                    ', '.join(str(state) for state in invalid_states)))

    def copy(self) -> 'Automaton':
        """Create a deep copy of the automaton."""
        automaton_copy = self.__class__()
        for att in self.__dict__:
            setattr(automaton_copy, att, deepcopy(getattr(self, att)))
        return automaton_copy

    def __eq__(self, other):
        """Check if two automata are equal."""
        return vars(self) == vars(other)
