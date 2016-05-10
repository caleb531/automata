#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc


class TM(metaclass=abc.ABCMeta):
    """An abstract base class for Turing machines."""

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """Initialize a complete Turing machine."""
        pass

    def _validate_input_symbol_subset(self):
        if not (self.input_symbols < self.tape_symbols):
            raise MissingSymbolError(
                'The set of tape symbols is missing symbols from the input '
                'symbol set ({})'.format(
                    self.tape_symbols - self.input_symbols))

    def _validate_initial_state(self):
        """Raise an error if an initial state is invalid."""
        if self.initial_state not in self.states:
            raise InvalidStateError(
                '{} is not a valid initial state'.format(self.initial_state))

    def _validate_final_states(self):
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise InvalidStateError(
                'final states are not valid ({})'.format(
                    ', '.join(invalid_states)))

    def _validate_nonfinal_initial_state(self):
        """Raise an error if the initial state is a final state."""
        if self.initial_state in self.final_states:
            raise FinalStateError(
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


class TMError(Exception):
    """The base class for all machine-related errors."""

    pass


class InvalidStateError(TMError):
    """A state is not a valid state for this machine."""

    pass


class InvalidSymbolError(TMError):
    """A symbol is not a valid symbol for this machine."""

    pass


class InvalidDirectionError(TMError):
    """A direction is not a valid direction for this machine."""

    pass


class MissingSymbolError(TMError):
    """Symbols are missing from the machine definition."""

    pass


class FinalStateError(TMError):
    """The initial state is a final state."""

    pass


class RejectionError(TMError):
    """The machine halted on a non-final state."""

    pass
