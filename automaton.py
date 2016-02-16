#!/usr/bin/env python3

import abc


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
    """a state is missing from the transition function"""
    pass


class MissingSymbolError(AutomatonError):
    """a symbol is missing from the transition function"""
    pass


class FinalStateError(AutomatonError):
    """the automaton stopped at a non-final state"""
    pass


class Automaton(metaclass=abc.ABCMeta):

    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """initialize a complete finite automaton"""
        self.states = states
        self.symbols = symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.validate_automaton()

    @abc.abstractmethod
    def validate_input(self):
        pass

    @abc.abstractmethod
    def validate_automaton(self):
        pass
