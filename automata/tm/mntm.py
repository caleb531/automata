#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic Turing machines."""

from collections import deque
import copy

import automata.base.exceptions as exceptions
import automata.tm.ntm as tm
from automata.tm.tape import TMTape


class MNTM(tm.NTM):
    """A multitape nondeterministic Turing machine."""

    def __init__(self, *, states, input_symbols, tape_symbols, n_tapes,
                 transitions, initial_state, blank_symbol,
                 final_states):
        """Initialize a complete Turing machine."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.tape_symbols = tape_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.final_states = final_states.copy()
        # self.validate()

        self.tapes = [TMTape(
            self.blank_symbol, blank_symbol=self.blank_symbol) for _ in range(n_tapes)]
        self.current_state = self.initial_state

    def _restart_configuration(self, input_str):
        self.current_state = self.initial_state
        # Input is saved on first tape
        self.tapes[0] = self.tapes[0].load_symbols(input_str, 0)
        for tape in self.tapes[1:]:  # The rest of the tapes have blanks
            tape = tape.load_symbols(self.blank_symbol, 0)

    def _read_current_tape_symbols(self):
        return tuple(tape.read_symbol() for tape in self.tapes)

    def _get_transition(self):
        """Get the transiton tuple for the given state and tape symbols in each tape."""
        if self.current_state in self.transitions:
            return self.transitions[self.current_state][self._read_current_tape_symbols()]
        else:
            return None

    def _get_next_configuration(self, old_config):
        """Advance to the next configuration."""
        self.current_state, moves = old_config
        i = 0
        for tape, move in zip(self.tapes, moves):
            symbol, direction = move
            self.tapes[i] = tape.write_symbol(symbol)
            self.tapes[i] = self.tapes[i].move(direction)
            i += 1
        return self

    def _has_accepted(self):
        return self.current_state in self.final_states

    def read_input_stepwise(self, input_str):
        """
        Checks if the given string is accepted by this Turing machine, using a BFS of every
        possible configuration from each configuration.

        Yield the current configuration of the machine at each step.
        """
        self._restart_configuration(input_str)
        queue = deque([self])
        while len(queue) > 0:
            current_tm = queue.popleft()
            yield current_tm

            possible_transitions = current_tm._get_transition()
            if possible_transitions is None:
                if current_tm._has_accepted():
                    return current_tm
            else:
                for transition in possible_transitions[1:]:
                    queue.append(current_tm.copy(
                    )._get_next_configuration(transition))

                executed = current_tm._get_next_configuration(
                    possible_transitions[0])
                queue.append(executed)
                yield executed

        raise exceptions.RejectionException(
            'the multitape NTM did not reach an accepting configuration'
        )

    def __str__(self):
        description = ""
        for tape in self.tapes:
            description += f"{self.current_state} : {str(tape)}\n"
        return description
