#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc

import automata.shared.exceptions as exceptions
import automata.tm.exceptions as tmexceptions


class TM(metaclass=abc.ABCMeta):
    """An abstract base class for Turing machines."""

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """Initialize a complete Turing machine."""
        pass

    def _validate_input_symbol_subset(self):
        if not (self.input_symbols < self.tape_symbols):
            raise exceptions.MissingSymbolError(
                'The set of tape symbols is missing symbols from the input '
                'symbol set ({})'.format(
                    self.tape_symbols - self.input_symbols))

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

    def _validate_nonfinal_initial_state(self):
        """Raise an error if the initial state is a final state."""
        if self.initial_state in self.final_states:
            raise tmexceptions.InitialStateError(
                'initial state {} cannot be a final state'.format(
                    self.initial_state))

    @abc.abstractmethod
    def validate_self(self):
        """Return True if this machine is internally consistent."""
        pass

    @abc.abstractmethod
    def validate_input(self, input_str):
        """Check if the given string is accepted by this machine."""
        pass

    def copy(self):
        """Create an exact copy of the TM."""
        return self.__class__(self)

    def __eq__(self, other):
        """Check if two machines are equal."""
        return self.__dict__ == other.__dict__
