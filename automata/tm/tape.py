#!/usr/bin/env python3
"""Classes and methods for working with Turing machine tapes."""


class TMTape(object):
    """A Turing machine tape."""

    def __init__(self, tape, *, blank_symbol, current_position=0,
                 position_offset=0):
        """Initialize a new Turing machine tape."""
        self.tape = list(tape)
        self.blank_symbol = blank_symbol
        self.current_position = current_position
        self.position_offset = position_offset

    def read_symbol(self):
        """Read the symbol at the current position in the tape."""
        actual_position = self.current_position + self.position_offset
        if actual_position == -1 or actual_position == len(self.tape):
            return self.blank_symbol
        else:
            return self.tape[actual_position]

    def write_symbol(self, new_tape_symbol):
        """Write the given symbol at the current position in the tape."""
        actual_position = self.current_position + self.position_offset
        if actual_position == -1:
            self.tape.insert(0, new_tape_symbol)
            self.position_offset += 1
        elif actual_position == len(self.tape):
            self.tape.append(new_tape_symbol)
        else:
            self.tape[actual_position] = new_tape_symbol

    def move(self, direction):
        """Move the tape to the next symbol in the given direction."""
        if direction == 'R':
            self.current_position += 1
        elif direction == 'N':
            pass
        elif direction == 'L':  # pragma: no branch
            self.current_position -= 1

    def copy(self):
        """Return a deep copy of the tape."""
        return self.__class__(**self.__dict__)

    def __len__(self):
        """Return the number of symbols on the tape."""
        return len(self.tape)

    def __iter__(self):
        """Return an interator for the tape."""
        return iter(self.tape)

    def __repr__(self):
        """Return a string representation of the tape."""
        return '{}(\'{}\')'.format(self.__class__.__name__, ''.join(self.tape))

    def __eq__(self, other):
        """Check if two tapes are equal."""
        return self.__dict__ == other.__dict__
