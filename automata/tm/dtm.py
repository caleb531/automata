#!/usr/bin/env python3
"""Classes and methods for working with Turing machines."""

import copy

import automata.tm.tm as tm
import automata.shared.exceptions as exceptions
import automata.tm.exceptions as tmexceptions
from automata.tm.tape import TMTape


class DTM(tm.TM):
    """A deterministic Turing machine."""

    def __init__(self, obj=None, **kwargs):
        """Initialize a complete Turing machine."""
        if isinstance(obj, DTM):
            self._init_from_dtm(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, tape_symbols,
                                 transitions, initial_state, blank_symbol,
                                 final_states):
        """Initialize a DTM from the formal definition parameters."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.tape_symbols = tape_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.final_states = final_states.copy()
        self.validate_self()

    def _init_from_dtm(self, tm):
        """Initialize this DTM as a deep copy of the given DTM."""
        self.__init__(
            states=tm.states, input_symbols=tm.input_symbols,
            tape_symbols=tm.tape_symbols, transitions=tm.transitions,
            initial_state=tm.initial_state, blank_symbol=tm.blank_symbol,
            final_states=tm.final_states)

    def _validate_transition_state(self, transition_state):
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                'transition state is not valid ({})'.format(transition_state))

    def _validate_transition_symbols(self, state, paths):
        for tape_symbol in paths.keys():
            if tape_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    'transition symbol {} for state {} is not valid'.format(
                        tape_symbol, state))

    def _validate_transition_result_direction(self, result_direction):
        if not (result_direction == 'L' or result_direction == 'R'):
            raise tmexceptions.InvalidDirectionError(
                'result direction is not valid ({})'.format(
                    result_direction))

    def _validate_transition_result(self, result):
        result_state, result_symbol, result_direction = result
        if result_state not in self.states:
            raise exceptions.InvalidStateError(
                'result state is not valid ({})'.format(result_state))
        if result_symbol not in self.tape_symbols:
            raise exceptions.InvalidSymbolError(
                'result symbol is not valid ({})'.format(result_symbol))
        self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, paths):
        for result in paths.values():
            self._validate_transition_result(result)

    def _validate_transitions(self):
        for state, paths in self.transitions.items():
            self._validate_transition_state(state)
            self._validate_transition_symbols(state, paths)
            self._validate_transition_results(paths)

    def _validate_final_state_transitions(self):
        for final_state in self.final_states:
            if final_state in self.transitions:
                raise exceptions.FinalStateError(
                    'final state {} has transitions defined'.format(
                        final_state))

    def validate_self(self):
        """Return True if this DTM is internally consistent."""
        self._validate_input_symbol_subset()
        self._validate_transitions()
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_nonfinal_initial_state()
        self._validate_final_states()
        self._validate_final_state_transitions()
        return True

    def _get_transition(self, state, tape_symbol):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            return self.transitions[state][tape_symbol]
        else:
            raise exceptions.RejectionError(
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
        tape = TMTape(input_str, blank_symbol=self.blank_symbol)
        yield current_state, tape

        # The initial state cannot be a final state for a DTM, so the first
        # iteration is always guaranteed to run (as it should)
        while current_state not in self.final_states:

            input_symbol = tape.read_symbol()
            (current_state, new_tape_symbol,
                current_direction) = self._get_transition(
                    current_state, input_symbol)
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)

            yield current_state, tape
