#!/usr/bin/env python3
"""Exception classes shared by all automata."""


class AutomatonError(Exception):
    """The base class for all automaton-related errors."""

    pass


class InvalidStateError(AutomatonError):
    """A state is not a valid state for this FA."""

    pass


class InvalidSymbolError(AutomatonError):
    """A symbol is not a valid symbol for this FA."""

    pass


class MissingStateError(AutomatonError):
    """A state is missing from the machine definition."""

    pass


class MissingSymbolError(AutomatonError):
    """A symbol is missing from the machine definition."""

    pass


class RejectionError(AutomatonError):
    """The FA stopped on a non-final state."""

    pass
