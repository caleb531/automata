#!/usr/bin/env python3
"""Exception classes specific to Turing machines."""

from automata.base.exceptions import AutomatonException


class TMException(AutomatonException):
    """The base class for all machine-related errors."""

    pass


class InvalidDirectionError(TMException):
    """A direction is not a valid direction for this machine."""

    pass
