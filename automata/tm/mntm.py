#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic Turing machines."""

from collections import deque
import copy

import automata.base.exceptions as exceptions
import automata.tm.ntm as tm
from automata.tm.tape import TMTape
from automata.tm.configuration import TMConfiguration, MTMConfiguration


class MNTM(tm.NTM):
    """A multitape nondeterministic Turing machine."""

    def __init__(
        self,
        *,
        states,
        input_symbols,
        tape_symbols,
        n_tapes,
        transitions,
        initial_state,
        blank_symbol,
        final_states
    ):
        """Initialize a complete Turing machine."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.tape_symbols = tape_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.final_states = final_states.copy()
        self.validate()
        self.head_symbol = "^"
        self.tape_separator_symbol = "_"

        self.tapes = [
            TMTape(self.blank_symbol, blank_symbol=self.blank_symbol)
            for _ in range(n_tapes)
        ]
        self.current_state = self.initial_state
        self.steps_as_mntm = 0
        self.steps_as_ntm = 0

    def _validate_transition_symbols(self, state, paths):
        for tape_symbol in [
            tape_symbol for symbol in paths.keys() for tape_symbol in symbol
        ]:
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

    def _restart_configuration(self, input_str):
        self.steps_as_mntm = 0
        self.steps_as_ntm = 0
        self.current_state = self.initial_state
        # Input is saved on first tape
        self.tapes[0] = self.tapes[0].load_symbols(input_str, 0)
        for i, tape in enumerate(self.tapes[1:]):  # The rest of the tapes have blanks
            self.tapes[i + 1] = tape.load_symbols(self.blank_symbol, 0)

    def _read_current_tape_symbols(self):
        return tuple(tape.read_symbol() for tape in self.tapes)

    def _get_transition(self):
        """Get the transiton tuple for the given state and tape symbols in 
        each tape."""
        if self.current_state in self.transitions:
            return self.transitions[self.current_state][
                self._read_current_tape_symbols()
            ]
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
        self.steps_as_mntm += 2 * i  # 1 write operation and 1 move operation
        return self

    def _has_accepted(self):
        return self.current_state in self.final_states

    def accepts(self, input_str):
        try:
            self.read_input_stepwise(input_str)
            return True
        except:
            return False

    def read_input_stepwise(self, input_str):
        """Checks if the given string is accepted by this Turing machine,
        using a BFS of every possible configuration from each configuration.
        
        Yields the current configuration of the machine at each step.
        """
        self._restart_configuration(input_str)
        queue = deque([self])  # Double end queue data structure
        # As long as there are possible sub-Turing machines to visit
        while len(queue) > 0:
            # Gets the current sub-Turing machine
            current_tm = queue.popleft()
            yield current_tm

            # Using the current state and the current tape symbols (got by calling
            # _read_current_tape_symbols), the transitions are obtained. If they are
            # None (there are no more transitions from this state) and the current
            # state is a final state, the machine accepts. If there are indeed more
            # transitions, the machine loops through them and appends the next
            # configuration of each of the transitions (or sub-Turing machines).
            possible_transitions = current_tm._get_transition()
            if possible_transitions is None:
                if current_tm._has_accepted():
                    return current_tm
            else:
                for transition in possible_transitions[1:]:
                    queue.append(current_tm.copy()._get_next_configuration(transition))

                executed = current_tm._get_next_configuration(possible_transitions[0])
                queue.append(executed)
                # yield executed

        raise exceptions.RejectionException(
            "the multitape NTM did not reach an accepting configuration"
        )

    def _read_extended_tape(self, tape: str):
        """Returns a tuple with the symbols extracted from the given
        tape, that are the virtual heads for their corresponding
        virtual tape.
        """
        virtual_heads = []
        for i in range(len(tape)):
            self.steps_as_ntm += 1
            if tape[i] == self.head_symbol:
                virtual_heads.append(tape[i - 1])

        return tuple(virtual_heads)

    def simulate_as_ntm(self, input_str):
        """Simulates the machine as a single-tape turing machine.
        Yields the configuration at each step."""
        # Restarts important variables and builds an extended tape given by
        # first-tape#second_tape#third_tape#...
        # Each tape has one 'head symbol', denoted as '^', which indicates the position of a
        # 'virtual head'. In other words, this extended tape has a particular symbol that indicates
        # the head of each tape, so that, if the machine reads the entire extended tape, it can
        # infer which symbols are currently been read on each tape.
        self._restart_configuration(input_str)
        extended_tape = ""
        tapes_copy = self.tapes.copy()
        for tape_copy in tapes_copy:
            tape_str = tape_copy.get_symbols_as_str()
            extended_tape += (
                tape_str[0]
                + self.head_symbol
                + tape_str[1:]
                + self.tape_separator_symbol
            )

        # Steps needed to build the extended tape. There are 2 blank symbols for each tape (except
        # for the first one).
        self.steps_as_ntm += 2 * len(self.tapes) - 1
        current_state = self.current_state
        yield {
            TMConfiguration(
                current_state,
                TMTape(
                    extended_tape, blank_symbol=self.blank_symbol, current_position=0
                ),
            )
        }

        # If the machine has not reached an accepting state.
        while current_state not in self.final_states:
            i = 0  # current position
            virtual_heads = self._read_extended_tape(extended_tape)
            try:
                next_config = self.transitions[current_state][virtual_heads]
            except KeyError:
                raise exceptions.RejectionException(
                    "the multitape NTM did not reach an accepting configuration"
                )
            next_state, moves = next_config[0]
            for move in moves:
                # * new_head is the symbol that must be written on top of one of the 'virtual head's.
                # * direction is the direction to which the 'virtual head' will be positioned.
                new_head, direction = move
                executing_changes = True

                # This loops through one of the virtual tapes in the entire extended tape looking
                # for the 'virtual head' of the tape the machine is looping through.
                # If the tape separator symbol is found (usually '#'), that means that this
                # has already looped through one of the virtual tapes, thus it breaks the loop and
                # executes the next move (associated with the next virtual tape).
                while executing_changes:
                    if extended_tape[i] == self.head_symbol:
                        # Head has been found (previous symbol is the head).
                        # This replaces the previous symbol with the new_head.
                        self.steps_as_ntm += 1  # 1 write operation
                        extended_tape = (
                            extended_tape[: i - 1] + new_head + extended_tape[i:]
                        )
                        extended_tape = extended_tape[:i] + "" + extended_tape[i + 1 :]

                        # After replacing, the machine must change the position of the virtual head
                        # of the current virtual tape.
                        if direction == "R":
                            i += 1
                        elif direction == "L":
                            i -= 1
                        else:  # direction == 'N'
                            i += 0

                        # In case one shift operation must be executed (this happens if the virtual
                        # head of one of the virtual tapes runs out of space, i.e has reached the
                        # rightmost end of the tape).
                        if extended_tape[i - 1] == self.tape_separator_symbol:
                            # Shift operation. 1 insertion and the rest are moves required for
                            # shifting extended_tape from i-th position to the right
                            self.steps_as_ntm += 1 + 4 * (len(extended_tape) - i) + 2
                            i -= 1
                            extended_tape = (
                                extended_tape[:i]
                                + self.blank_symbol
                                + self.head_symbol
                                + extended_tape[i:]
                            )

                            i += 1
                        else:
                            # 1 move operation if virtual head changes to the right or the left
                            if direction != "N":
                                self.steps_as_ntm += 1
                            # 1 write operation
                            self.steps_as_ntm += 1
                            extended_tape = (
                                extended_tape[:i] + self.head_symbol + extended_tape[i:]
                            )

                    elif extended_tape[i] == self.tape_separator_symbol:
                        executing_changes = False

                    i += 1

            current_state = next_state
            yield {
                TMConfiguration(
                    current_state,
                    TMTape(
                        extended_tape,
                        blank_symbol=self.blank_symbol,
                        current_position=i,
                    ),
                )
            }

    def __str__(self):
        config = MTMConfiguration(self.current_state, self.tapes)
        return config._description()
