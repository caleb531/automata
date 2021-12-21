#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc
import automata.base.exceptions as exceptions

from typing import Hashable, NoReturn, Generator, Set, Dict, Any, TypeVar
from copy import deepcopy

AutomatonStateT = Hashable
CopyT = TypeVar('CopyT')

class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    states : Set[AutomatonStateT]
    initial_state : AutomatonStateT
    final_states : Set[AutomatonStateT]
    transitions : Dict[AutomatonStateT, Any]

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

    def read_input(self, input_str : str) -> Any:
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

    def copy(self : CopyT) -> CopyT:
        """Create a deep copy of the automaton."""
        return self.__class__(**vars(self)) #type: ignore

    def __eq__(self, other : object) -> bool:
        """Check if two automata are equal."""
        if not isinstance(other, Automaton):
            return NotImplemented

        return vars(self) == vars(other)
