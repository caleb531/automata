#!/usr/bin/env python3
"""Classes and methods for working with PDA configurations."""

from dataclasses import dataclass

from automata.base.automaton import AutomatonStateT
from automata.pda.stack import PDAStack


@dataclass(frozen=True, slots=True)
class PDAConfiguration:
    """
    A configuration is a triple of current state, remaining input and stack.

    It represents the complete runtime state of a PDA.
    It is hashable and immutable.
    """

    state: AutomatonStateT
    remaining_input: str
    stack: PDAStack

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return "{}(state='{}', remaining_input='{}', stack={})".format(
            self.__class__.__name__, self.state, self.remaining_input, self.stack
        )
