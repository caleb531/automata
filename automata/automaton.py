#!/usr/bin/env python3

import abc


class Automaton(metaclass=abc.ABCMeta):
    """an abstract base class for finite automata"""

    @abc.abstractmethod
    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """initializes a complete finite automaton"""
        pass

    @abc.abstractmethod
    def validate_automaton(self):
        """returns True if this automaton is internally consistent;
        raises the appropriate exception otherwise"""
        pass

    def validate_transition_start_states(self):
        """raises an error if this automaton's transition start states are
        missing"""
        missing_states = self.states - set(self.transitions.keys())
        if missing_states:
            raise MissingStateError(
                'states are missing from transition map ({})'.format(
                    ', '.join(missing_states)))

    def validate_transition_end_states(self, path_states):
        """raises an error if this automaton's transition end states are
        invalid"""
        invalid_states = path_states - self.states
        if invalid_states:
            raise InvalidStateError(
                'states are not valid ({})'.format(', '.join(invalid_states)))

    def validate_initial_state(self):
        """raises an error if this automaton's initial state is invalid"""
        if self.initial_state not in self.states:
            raise InvalidStateError(
                '{} is not a valid state'.format(self.initial_state))

    def validate_final_states(self):
        """raises an error if this automaton's final states are invalid"""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise InvalidStateError(
                'states are not valid ({})'.format(', '.join(invalid_states)))

    @abc.abstractmethod
    def validate_input(self, input_str):
        """returns True if the given string is accepted by this automaton;
        raises the appropriate exception otherwise"""
        pass

    def validate_input_symbol(self, symbol):
        """raises an error if the given input symbol is invalid"""
        if symbol not in self.symbols:
            raise InvalidSymbolError(
                '{} is not a valid symbol'.format(symbol))

    @staticmethod
    def stringify_states(states):
        """stringifies the given set of states as a single state name"""
        return '{{{}}}'.format(''.join(sorted(states)))


class AutomatonError(Exception):
    """the base class for all automaton-related errors"""
    pass


class InvalidStateError(AutomatonError):
    """a state is not a valid state for this automaton"""
    pass


class InvalidSymbolError(AutomatonError):
    """a symbol is not a valid symbol for this automaton"""
    pass


class MissingStateError(AutomatonError):
    """a state is missing from the transition map"""
    pass


class MissingSymbolError(AutomatonError):
    """a symbol is missing from the transition map"""
    pass


class FinalStateError(AutomatonError):
    """the automaton stopped at a non-final state"""
    pass
