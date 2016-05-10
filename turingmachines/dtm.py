#!/usr/bin/env python3
"""Classes and methods for working with Turing machines."""

import copy

import turingmachines.tm as tm
from turingmachines.tape import TMTape


class DTM(tm.TM):
    """A deterministic Turing machine."""

    def __init__(self, obj=None, *, states=None, input_symbols=None,
                 tape_symbols=None, transitions=None, initial_state=None,
                 blank_symbol=None, final_states=None):
        """Initialize a complete Turing machine."""
        if isinstance(obj, DTM):
            self._init_from_dtm(obj)
        else:
            self.states = states.copy()
            self.input_symbols = input_symbols.copy()
            self.tape_symbols = tape_symbols.copy()
            self.transitions = copy.deepcopy(transitions)
            self.initial_state = initial_state
            self.blank_symbol = blank_symbol
            self.final_states = final_states.copy()
            self.validate_self()

    def _init_from_dtm(self, tm):
        """Initialize this DTM as an exact copy of the given DTM."""
        self.__init__(
            states=tm.states, input_symbols=tm.input_symbols,
            tape_symbols=tm.tape_symbols, transitions=tm.transitions,
            initial_state=tm.initial_state, blank_symbol=tm.blank_symbol,
            final_states=tm.final_states)

    def validate_self(self):
        """Return True if this DTM is internally consistent."""
        self._validate_initial_state()
        self._validate_final_states()

    def _get_transition(self, state, tape_symbol):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            return self.transitions[state][tape_symbol]
        else:
            raise tm.RejectionError(
                'The machine entered a non-final configuration for which no '
                'transition is defined ({}, {})'.format(
                    state, tape_symbol))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this Turing machine.

        Yield the current configuration of the machine at each step.
        """
        current_state = self.initial_state
        current_direction = None
        tape = TMTape(
            tape=input_str, blank_symbol=self.blank_symbol)
        yield current_state, tape

        while True:

            input_symbol = tape.read_symbol()
            (current_state, new_tape_symbol,
                current_direction) = self._get_transition(
                    current_state, input_symbol)
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)

            yield current_state, tape
            if current_state in self.final_states:
                return

    def _validate_input_return(self, input_str):
        """
        Check if the given string is accepted by this Turing machine.

        Return the state the machine stopped on if the string is valid.
        """
        validation_generator = self._validate_input_yield(input_str)
        for current_state, tape in validation_generator:
            pass
        return current_state, tape

    def validate_input(self, input_str, step=False):
        """
        Check if the given string is accepted by this Turing machine.

        If step is True, yield the configuration at each step. Otherwise,
        return the final configuration.
        """
        if step:
            return self._validate_input_yield(input_str)
        else:
            return self._validate_input_return(input_str)
