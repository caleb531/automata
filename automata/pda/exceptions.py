#!/usr/bin/env python3
"""Exception classes specific to pushdown automata."""

from automata.base.exceptions import AutomatonException


class PDAException(AutomatonException):
    """The base class for all PDA-related errors."""

    pass


class NondeterminismError(PDAException):
    """A DPDA is exhibiting nondeterminism."""

    pass

class InvalidAcceptanceMode(PDAException):
    """The given acceptance mode is invalid."""
    pass
