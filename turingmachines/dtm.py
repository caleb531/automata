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

    def _validate_transition_state(self, transition_state):
        if transition_state not in self.states:
            raise tm.InvalidStateError(
                'transition state is not valid ({})'.format(transition_state))

    def _validate_transition_symbols(self, transition_symbols):
        invalid_states = transition_symbols - self.tape_symbols
        if invalid_states:
            raise tm.InvalidSymbolError(
                'transition symbols are not valid ({})'.format(
                    ', '.join(invalid_states)))

    def _validate_transition_result_direction(self, result_direction):
        if not (result_direction == 'L' or result_direction == 'R'):
            raise tm.InvalidDirectionError(
                'result direction is not valid ({})'.format(
                    result_direction))

    def _validate_transition_result(self, result):
        result_state, result_symbol, result_direction = result
        if result_state not in self.states:
            raise tm.InvalidStateError(
                'result state is not valid ({})'.format(result_state))
        if result_symbol not in self.tape_symbols:
            raise tm.InvalidSymbolError(
                'result symbol is not valid ({})'.format(result_symbol))
        self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, results):
        for result in results:
            self._validate_transition_result(result)

    def _validate_transitions(self):
        for state, transition_symbols in self.transitions.items():
            self._validate_transition_state(state)
            self._validate_transition_symbols(set(transition_symbols.keys()))
            self._validate_transition_results(set(transition_symbols.values()))

    def validate_self(self):
        """Return True if this DTM is internally consistent."""
        self._validate_input_symbol_subset()
        self._validate_transitions()
        self._validate_initial_state()
        self._validate_final_states()
        self._validate_nonfinal_initial_state()
        return True

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
