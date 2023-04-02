#!/usr/bin/env python3
"""Classes and methods for working with Turing machine tapes."""

import collections
from typing import Iterator, Sequence, Tuple

from typing_extensions import Self

from automata.tm.tm import TMDirectionT


class TMTape(
    collections.namedtuple("TMTape", ["tape", "blank_symbol", "current_position"])
):
    """A Turing machine tape."""

    tape: Tuple[str]
    blank_symbol: str
    current_position: int

    def __new__(
        cls, tape: Sequence[str], *, blank_symbol: str, current_position: int = 0
    ):
        """Initialize a new Turing machine tape."""
        tape = list(tape)
        # Make sure that there's something under the cursor.
        while len(tape) <= current_position:
            tape.append(blank_symbol)
        tape = tuple(tape)
        return super(TMTape, cls).__new__(cls, tape, blank_symbol, current_position)

    def read_symbol(self) -> str:
        """Read the symbol at the current position in the tape."""
        return self.tape[self.current_position]

    def write_symbol(self, new_tape_symbol: str) -> Self:
        """Write the given symbol at the current position in the tape."""
        tape_elements = list(self.tape)
        tape_elements[self.current_position] = new_tape_symbol
        return self.__class__(
            tape_elements,
            blank_symbol=self.blank_symbol,
            current_position=self.current_position,
        )

    def move(self, direction: TMDirectionT) -> Self:
        """Move the tape to the next symbol in the given direction."""
        # Copy stuff.
        new_tape = list(self.tape)
        new_position = self.current_position
        if direction == "R":
            new_position += 1
        elif direction == "N":
            pass
        elif direction == "L":  # pragma: no branch
            new_position -= 1
        # Make sure that the cursor doesn't run off the end of the tape.
        if new_position == -1:
            new_tape.insert(0, self.blank_symbol)
            new_position += 1
        if new_position == len(new_tape):
            new_tape.append(self.blank_symbol)
        return self.__class__(
            new_tape, blank_symbol=self.blank_symbol, current_position=new_position
        )

    def copy(self) -> Self:
        return self.__class__(
            list(self.tape).copy(),
            blank_symbol=self.blank_symbol,
            current_position=self.current_position,
        )

    def get_symbols_as_str(self) -> str:
        return "".join(self.tape)

    def __len__(self) -> int:
        """Return the number of symbols on the tape."""
        return len(self.tape)  # TODO: do we count the blank symbols?

    def __iter__(self) -> Iterator[str]:
        """Return an interator for the tape."""
        return iter(self.tape)

    def __repr__(self) -> str:
        """Return a string representation of the tape."""
        return "{}('{}', {})".format(
            self.__class__.__name__, "".join(self.tape), self.current_position
        )
