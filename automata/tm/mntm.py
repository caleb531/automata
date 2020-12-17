#!/usr/bin/env python3
"""Classes and methods for working with multitape nondeterministic Turing
machines."""

import copy
from collections import deque

import automata.base.exceptions as exceptions
import automata.tm.ntm as tm
from automata.tm.configuration import MTMConfiguration, TMConfiguration
from automata.tm.tape import TMTape


class MNTM(tm.NTM):
    """A multitape nondeterministic Turing machine."""

    def __init__(self, *, states, input_symbols, tape_symbols, n_tapes,
                 transitions, initial_state, blank_symbol, final_states,
                 tapes=None):
        """Initialize a complete Turing machine."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.tape_symbols = tape_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.final_states = final_states.copy()
        self.n_tapes = n_tapes

        if tapes is not None:
            self.tapes = tapes
        else:
            self.tapes = [
                TMTape(
                    self.blank_symbol, blank_symbol=self.blank_symbol)
                for _ in range(n_tapes)]

        self.validate()

    def _validate_transition_symbols(self, state, paths):
        for tape_symbol in [tape_symbol
                            for symbol in paths.keys() for tape_symbol in
                            symbol]:
            if tape_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    "transition symbol {} for state {} is not valid".format(
                        tape_symbol, state
                    )
                )

    def _validate_transition_state(self, transition_state):
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                "transition state is not valid ({})".format(transition_state)
            )

    def _validate_transition_results(self, paths):
        for results in paths.values():
            for result in results:
                state, moves = result
                for move in moves:
                    symbol, direction = move
                    possible_result = (state, symbol, direction)
                    self._validate_transition_result(possible_result)

    def _validate_tapes_consistency(self):
        for state in self.transitions:
            for read_tape_symbols in self.transitions[state]:
                if len(read_tape_symbols) != self.n_tapes:
                    raise exceptions.InconsistentTapesException(
                        f"tapes symbols {read_tape_symbols} is inconsistent with \
                        the number of tapes defined. Expected \
                        {self.n_tapes} symbols, got \
                        {len(read_tape_symbols)}")

                for transition in self.transitions[state][read_tape_symbols]:
                    _, moves = transition
                    if len(moves) != self.n_tapes:
                        raise exceptions.InconsistentTapesException(
                            f"transition {transition} has inconsistent operations \
                            on tapes. Expected {self.n_tapes} write/move \
                            operations, got {len(moves)}")

    def validate(self):
        """Return True if this MNTM is internally consistent."""
        super().validate()
        self._validate_tapes_consistency()
        return True

    def _restart_configuration(self, input_str):
        """Restarts all variables so that the Turing machine can be used
        again with a new input string."""
        # Input is saved on first tape
        self.tapes[0] = self.tapes[0].load_symbols(input_str, 0)
        # The rest of the tapes have blanks
        for i, tape in enumerate(self.tapes[1:]):
            self.tapes[i + 1] = tape.load_symbols(self.blank_symbol, 0)

    def _read_current_tape_symbols(self):
        """Reads the current tape symbols in each of the tapes and their
        corresponding heads."""
        return tuple(tape.read_symbol() for tape in self.tapes)

    def _get_transition(self, state):
        """Get the transiton tuple for the given state and tape symbols in
        each tape."""
        current_tape_symbols = self._read_current_tape_symbols()
        if state in self.transitions and current_tape_symbols in \
                self.transitions[state]:
            return self.transitions[state][self._read_current_tape_symbols()]
        else:
            return None

    def _get_next_configuration(self, old_config, return_state=False):
        """Advances to the next configuration."""
        state, moves = old_config
        i = 0
        for tape, move in zip(self.tapes, moves):
            symbol, direction = move
            self.tapes[i] = tape.write_symbol(symbol)
            self.tapes[i] = self.tapes[i].move(direction)
            i += 1

        if return_state:
            return self, state
        else:
            return self

    def _has_accepted(self, state):
        return state in self.final_states

    def read_input_stepwise(self, input_str):
        """Checks if the given string is accepted by this Turing machine,
        using a BFS of every possible configuration from each configuration.
        Yields the current configuration of the machine at each step.
        """
        self._restart_configuration(input_str)
        current_state = self.initial_state
        queue = deque([self])
        while len(queue) > 0:
            current_tm = queue.popleft()
            yield {MTMConfiguration(current_state, tuple(self.tapes))}

            possible_transitions = current_tm._get_transition(current_state)
            if possible_transitions is None:
                if current_tm._has_accepted(current_state):
                    return {MTMConfiguration(current_state, tuple(self.tapes))}
            else:
                for transition in possible_transitions[1:]:
                    queue.append(
                        current_tm.copy()._get_next_configuration(transition)
                    )

                executed, current_state = current_tm._get_next_configuration(
                    possible_transitions[0], return_state=True)
                queue.append(executed)

        raise exceptions.RejectionException(
            "the multitape NTM did not reach an accepting configuration"
        )

    def _read_extended_tape(self, tape: str, head_symbol: str):
        """Returns a tuple with the symbols extracted from the given
        tape, that are the virtual heads for their corresponding
        virtual tape."""
        virtual_heads = []
        for i in range(len(tape)):
            if tape[i] == head_symbol:
                virtual_heads.append(tape[i - 1])

        return tuple(virtual_heads)

    def simulate_as_ntm(self, input_str):
        """Simulates the machine as a single-tape Turing machine.
        Yields the configuration at each step."""
        self._restart_configuration(input_str)
        head_symbol = "^"
        tape_separator_symbol = "_"
        extended_tape = ""
        tapes_copy = self.tapes.copy()
        for tape_copy in tapes_copy:
            tape_str = tape_copy.get_symbols_as_str()
            extended_tape += tape_str[0] + head_symbol + \
                tape_str[1:] + tape_separator_symbol

        current_state = self.initial_state
        yield {
            TMConfiguration(current_state,
                            TMTape(extended_tape,
                                   blank_symbol=self.blank_symbol,
                                   current_position=0)
                            )
        }

        # If the machine has not reached an accepting state.
        while current_state not in self.final_states:
            i = 0  # current position
            virtual_heads = self._read_extended_tape(extended_tape,
                                                     head_symbol)
            try:
                next_config = self.transitions[current_state][virtual_heads]
            except KeyError:
                raise exceptions.RejectionException(
                    "the multitape NTM did not reach an accepting  \
                    configuration")
            next_state, moves = next_config[0]
            for move in moves:
                new_head, direction = move
                executing_changes = True

                while executing_changes:
                    if extended_tape[i] == head_symbol:
                        # Head has been found (previous symbol is the head).
                        # This replaces the previous symbol with the new_head.
                        extended_tape = (
                            extended_tape[: i - 1] +
                            new_head + extended_tape[i:]
                        )
                        extended_tape = extended_tape[:i] + \
                            "" + extended_tape[i + 1:]

                        # After replacing, the machine must change the
                        # position of the virtual head of the current virtual
                        # tape.
                        if direction == "R":
                            i += 1
                        elif direction == "L":
                            i -= 1
                        else:  # direction == 'N'
                            i += 0

                        if extended_tape[i - 1] == tape_separator_symbol:
                            i -= 1
                            extended_tape = extended_tape[:i]
                            + self.blank_symbol + \
                                head_symbol + extended_tape[i:]

                            i += 1
                        else:
                            extended_tape = (
                                extended_tape[:i] +
                                head_symbol + extended_tape[i:]
                            )

                    elif extended_tape[i] == tape_separator_symbol:
                        executing_changes = False

                    i += 1

            current_state = next_state
            yield {
                TMConfiguration(current_state,
                                TMTape(extended_tape,
                                       blank_symbol=self.blank_symbol,
                                       current_position=i)
                                )
            }
