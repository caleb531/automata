#!/usr/bin/env python3
"""Exception classes shared by all automata."""


class AutomatonException(Exception):
    """The base class for all automaton-related errors."""

    pass


class InvalidStateError(AutomatonException):
    """A state is not a valid state for this automaton."""

    pass


class InvalidSymbolError(AutomatonException):
    """A symbol is not a valid symbol for this automaton."""

    pass


class MissingStateError(AutomatonException):
    """A state is missing from the automaton definition."""

    pass


class MissingSymbolError(AutomatonException):
    """A symbol is missing from the automaton definition."""

    pass


class InitialStateError(AutomatonException):
    """The initial state fails to meet some required condition."""

    pass


class FinalStateError(AutomatonException):
    """A final state fails to meet some required condition."""

    pass


class RejectionException(AutomatonException):
    """The input was rejected by the automaton."""

    pass
