#!/usr/bin/env python3
"""Classes and methods for working with Turing machine configurations."""

from dataclasses import dataclass
from typing import List

from automata.tm.tape import TMTape
from automata.tm.tm import TMStateT


@dataclass(frozen=True)
class TMConfiguration:
    """A Turing machine configuration."""

    __slots__ = ("state", "tape")

    state: TMStateT
    tape: TMTape

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return "{}('{}', {})".format(self.__class__.__name__, self.state, self.tape)

    def print(self) -> None:
        """Print the machine's current configuration in a readable form."""
        print(
            "{current_state}: {tape}\n{current_position}".format(
                current_state=self.state,
                tape="".join(self.tape).rjust(len(self.tape), self.tape.blank_symbol),
                current_position="^".rjust(
                    self.tape.current_position + len(self.state) + 3
                ),
            )
        )


@dataclass(frozen=True)
class MTMConfiguration:
    """A Multitape Turing machine configuration."""

    __slots__ = ("state", "tapes")

    state: TMStateT
    tapes: List[TMTape]

    def __repr__(self) -> str:
        """Return a string representation of the configuration."""
        return "{}('{}', {})".format(self.__class__.__name__, self.state, self.tapes)

    def print(self) -> None:
        """Print the machine's current configuration in a readable form."""
        description = "{}: \n".format(self.state)
        for i, tape in enumerate(self.tapes, start=1):
            title = "> Tape {}: ".format(i)
            position = tape.current_position + len(title) + 1
            description += "> Tape {j}: {tape}\n{current_position}\n".format(
                j=i,
                tape="".join(tape).ljust(tape.current_position, "#"),
                current_position="^".rjust(position),
            )
        print(description)
