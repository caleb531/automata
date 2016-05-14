#!/usr/bin/env python3
"""Exception classes specific to pushdown automata."""

from automata.shared.exceptions import AutomatonError


class PDAError(AutomatonError):
    """The base class for all PDA-related errors."""

    pass


class NondeterminismError(PDAError):
    """A DPDA is exhibiting nondeterminism."""

    pass
