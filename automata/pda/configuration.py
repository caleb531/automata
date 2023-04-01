#!/usr/bin/env python3
"""Classes and methods for working with PDA configurations."""

from typing import Any, List, NamedTuple
from automata.pda.stack import PDAStack


class PDAConfiguration(NamedTuple):
    """
    A configuration is a triple of current state, remaining input and stack.

    It represents the complete runtime state of a PDA.
    It is hashable and immutable.
    """

    state: Any
    remaining_input: List[str]
    stack: PDAStack

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return "{}('{}', '{}', {})".format(
            self.__class__.__name__, self.state, self.remaining_input, self.stack
        )
