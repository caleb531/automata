#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    @abc.abstractmethod
    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """Initialize a complete finite automaton."""
        pass

    def _validate_transition_start_states(self):
        """Raise an error if transition start states are missing."""
        missing_states = self.states - set(self.transitions.keys())
        if missing_states:
            raise MissingStateError(
                'transition start states are missing ({})'.format(
                    ', '.join(missing_states)))

    def _validate_transition_end_states(self, path_states):
        """Raise an error if transition end states are invalid."""
        invalid_states = path_states - self.states
        if invalid_states:
            raise InvalidStateError(
                'transition end states are not valid ({})'.format(
                    ', '.join(invalid_states)))

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

    @abc.abstractmethod
    def validate_automaton(self):
        """Return True if this automaton is internally consistent."""
        pass

    def _validate_input_symbol(self, symbol):
        """Raise an error if the given input symbol is invalid."""
        if symbol not in self.symbols:
            raise InvalidSymbolError(
                '{} is not a valid input symbol'.format(symbol))

    @abc.abstractmethod
    def validate_input(self, input_str):
        """Check if the given string is accepted by this automaton."""
        pass

    @staticmethod
    def _stringify_states(states):
        if isinstance(states, set):
            states = sorted(states)
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(''.join(states))

    def copy(self):
        """Create an exact copy of the automaton."""
        return self.__class__(self)

    def complement(self):
        """Compute the complement of the automaton."""
        dfa_comp = self.__class__(self)
        dfa_comp.final_states = dfa_comp.states - dfa_comp.final_states
        return dfa_comp

    def __invert__(self):
        """Compute the complement of the automaton via the ~ operator."""
        return self.complement()

    def _validate_symbol_set_equality(self, other):
        """Raise an error if the symbol sets are not equal."""
        if other.symbols != self.symbols:
            raise SymbolMismatchError('symbol sets are not equal')


class AutomatonError(Exception):
    """The base class for all automaton-related errors."""

    pass


class InvalidStateError(AutomatonError):
    """A state is not a valid state for this automaton."""

    pass


class InvalidSymbolError(AutomatonError):
    """A symbol is not a valid symbol for this automaton."""

    pass


class MissingStateError(AutomatonError):
    """A state is missing from the transition map."""

    pass


class MissingSymbolError(AutomatonError):
    """A symbol is missing from the transition map."""

    pass


class FinalStateError(AutomatonError):
    """The automaton stopped at a non-final state."""

    pass


class SymbolMismatchError(AutomatonError):
    """The symbol sets for the automata are not equal."""

    pass
