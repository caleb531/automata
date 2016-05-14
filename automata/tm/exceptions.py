#!/usr/bin/env python3
"""Exception classes specific to Turing machines."""

from automata.shared.exceptions import AutomatonError


class TMError(AutomatonError):
    """The base class for all machine-related errors."""

    pass


class InvalidDirectionError(TMError):
    """A direction is not a valid direction for this machine."""

    pass
