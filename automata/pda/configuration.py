#!/usr/bin/env python3
"""Classes and methods for working with PDA configurations."""

from dataclasses import dataclass
from typing import Any

from automata.base.automaton import AutomatonStateT
from automata.pda.stack import PDAStack


@dataclass(frozen=True)
class PDAConfiguration:
    """
    A configuration is a triple of current state, remaining input and stack.

    It represents the complete runtime state of a PDA.
    It is hashable and immutable.
    """

    __slots__ = ("state", "remaining_input", "stack")

    state: AutomatonStateT
    remaining_input: str
    stack: PDAStack

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return "{}({!r}, {!r}, {!r})".format(
            self.__class__.__name__, self.state, self.remaining_input, self.stack
        )

    def __eq__(self, other: Any) -> bool:
        """Return True if two PDAConfiguration are equivalent"""
        if not isinstance(other, PDAConfiguration):
            raise NotImplemented

        if (
            self.state == other.state
            and self.remaining_input == other.remaining_input
            and self.stack == other.stack
        ):
            return True
        return False
