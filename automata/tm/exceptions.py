#!/usr/bin/env python3
"""Exception classes specific to Turing machines."""

from automata.base.exceptions import AutomatonException


class TMException(AutomatonException):
    """The base class for all machine-related errors."""

    pass


class InvalidDirectionError(TMException):
    """A direction is not a valid direction for this machine."""

    pass


class InconsistentTapesException(TMException):
    """The number of tapes defined for the multitape Turing machine is
    not consistent with the definitions of the transitions."""

    pass


class MalformedExtendedTapeError(TMException):
    """Extended tape for simulating an mntm as a ntm is not valid.
    Either there are 2 virtual heads for a virtual tape or the
    a head symbol is at the leftmost end of a virtual tape."""

    pass
