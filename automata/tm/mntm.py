#!/usr/bin/env python3
"""Classes and methods for working with multitape nondeterministic Turing
machines."""

from collections import deque
from typing import AbstractSet, List, Mapping, Optional, Sequence, Tuple

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import automata.tm.ntm as ntm
import automata.tm.tm as tm
from automata.tm.configuration import MTMConfiguration, TMConfiguration
from automata.tm.tape import TMTape

MNTMStateT = ntm.NTMStateT
MNTMPathResultT = Tuple[str, Tuple[Tuple[str, tm.TMDirectionT], ...]]
MNTMPathT = Mapping[Tuple[str, ...], Sequence[MNTMPathResultT]]
MNTMTransitionsT = Mapping[str, MNTMPathT]


class MNTM(ntm.NTM):
    """A multitape nondeterministic Turing machine."""

    __slots__ = (
        "states",
        "input_symbols",
        "tape_symbols",
        "n_tapes",
        "transitions",
        "initial_state",
        "blank_symbol",
        "final_states",
    )

    transitions: MNTMTransitionsT  # type: ignore
    n_tapes: int

    def __init__(
        self,
        *,
        states: AbstractSet[MNTMStateT],
        input_symbols: AbstractSet[str],
        tape_symbols: AbstractSet[str],
        n_tapes: int,
        transitions: MNTMTransitionsT,
        initial_state: MNTMStateT,
        blank_symbol: str,
        final_states: AbstractSet[MNTMStateT],
    ):
        """Initialize a complete Turing machine."""
        super(tm.TM, self).__init__(
            states=states,
            input_symbols=input_symbols,
            tape_symbols=tape_symbols,
            transitions=transitions,
            initial_state=initial_state,
            blank_symbol=blank_symbol,
            final_states=final_states,
            n_tapes=n_tapes,
        )

    def _validate_transition_symbols(self, state: MNTMStateT, paths: Mapping) -> None:
        for tape_symbol in [
            tape_symbol for symbol in paths.keys() for tape_symbol in symbol
        ]:
            if tape_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    "transition symbol {} for state {} is not valid".format(
                        tape_symbol, state
                    )
                )

    def _validate_transition_state(self, transition_state: MNTMStateT) -> None:
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                "transition state is not valid ({})".format(transition_state)
            )

    def _validate_transition_results(self, paths: Mapping) -> None:
        for results in paths.values():
            for result in results:
                state, moves = result
                for move in moves:
                    symbol, direction = move
                    possible_result = (state, symbol, direction)
                    self._validate_transition_result(possible_result)

    def _validate_tapes_consistency(self) -> None:
        for state in self.transitions:
            for read_tape_symbols in self.transitions[state]:
                if len(read_tape_symbols) != self.n_tapes:
                    error = (
                        "tapes symbols {} inconsistent with the number of "
                        "tapes defined. Expected {} symbols, got {}"
                    ).format(read_tape_symbols, self.n_tapes, len(read_tape_symbols))
                    raise tm_exceptions.InconsistentTapesException(error)
                for transition in self.transitions[state][read_tape_symbols]:
                    _, moves = transition
                    if len(moves) != self.n_tapes:
                        error = (
                            "transition {} has inconsistent operations on "
                            "tapes. Expected {} write/move operations, "
                            "got {}"
                        ).format(transition, self.n_tapes, len(moves))
                        raise tm_exceptions.InconsistentTapesException(error)

    def validate(self) -> None:
        """Return True if this MNTM is internally consistent."""
        super().validate()
        self._validate_tapes_consistency()

    def _get_tapes_for_input_str(self, input_str: str) -> List[TMTape]:
        """Produce a new list of tapes based on an input string to be read."""
        return [
            # Input is saved on first tape
            TMTape(input_str, blank_symbol=self.blank_symbol),
            # The rest of the tapes have blanks
            *(
                TMTape(
                    self.blank_symbol,
                    blank_symbol=self.blank_symbol,
                    current_position=0,
                )
                for _ in range(self.n_tapes - 1)
            ),
        ]

    def _read_current_tape_symbols(self, tapes: Tuple[TMTape, ...]) -> Tuple[str, ...]:
        """Reads the current tape symbols in each of the tapes and their
        corresponding heads."""
        return tuple(tape.read_symbol() for tape in tapes)

    def _get_transition(
        self, current_state: MNTMStateT, tapes: Tuple[TMTape, ...]
    ) -> Optional[Sequence[MNTMPathResultT]]:
        """Get the transition tuple for the given state and tape symbols in
        each tape."""
        current_tape_symbols = self._read_current_tape_symbols(tapes)
        if (
            current_state in self.transitions
            and current_tape_symbols in self.transitions[current_state]
        ):
            return self.transitions[current_state][
                self._read_current_tape_symbols(tapes)
            ]
        else:
            return None

    def _get_next_configuration(self, transition, current_tapes):
        """Advances to the next configuration."""
        current_state, moves = transition
        tapes = current_tapes.copy()
        for i, move in enumerate(moves):
            symbol, direction = move
            tapes[i] = tapes[i].write_symbol(symbol)
            tapes[i] = tapes[i].move(direction)

        return MTMConfiguration(state=current_state, tapes=tapes)

    def _has_accepted(self, current_config):
        return current_config.state in self.final_states

    def read_input_stepwise(self, input_str):
        """Checks if the given string is accepted by this Turing machine,
        using a BFS of every possible configuration from each configuration.
        Yields the current configuration of the machine at each step.
        """
        tapes = self._get_tapes_for_input_str(input_str)
        queue = deque([(MTMConfiguration(state=self.initial_state, tapes=tapes[:]))])
        while len(queue) > 0:
            current_config = queue.popleft()
            yield {MTMConfiguration(current_config.state, tuple(current_config.tapes))}

            possible_transitions = self._get_transition(
                current_config.state, current_config.tapes
            )
            if possible_transitions is None:
                if self._has_accepted(current_config):
                    return {
                        MTMConfiguration(
                            current_config.state, tuple(current_config.tapes)
                        )
                    }
            else:
                for transition in possible_transitions[1:]:
                    queue.append(
                        self._get_next_configuration(
                            transition, current_tapes=current_config.tapes
                        )
                    )

                queue.append(
                    self._get_next_configuration(
                        possible_transitions[0], current_tapes=current_config.tapes
                    )
                )

        raise exceptions.RejectionException(
            "the multitape MNTM did not reach an accepting configuration"
        )

    @staticmethod
    def _read_extended_tape(
        tape: str, head_symbol: str = "^", tape_separator_symbol: str = "_"
    ):
        """Returns a tuple with the symbols extracted from the given
        tape, that are the virtual heads for their corresponding
        virtual tape."""
        virtual_heads = []
        heads_found = 0
        separators_found = 0
        for i, symbol in enumerate(tape):
            if symbol == head_symbol:
                if i - 1 < 0:
                    raise tm_exceptions.MalformedExtendedTapeError(
                        "head symbol was found on leftmost end of the " "extended tape"
                    )
                else:
                    previous_symbol = tape[i - 1]
                    virtual_heads.append(previous_symbol)
                    heads_found += 1
            elif symbol == tape_separator_symbol:
                if heads_found == 0:
                    raise tm_exceptions.MalformedExtendedTapeError(
                        "no head symbol found on one of the virtual tapes"
                    )
                elif heads_found > 1:
                    raise tm_exceptions.MalformedExtendedTapeError(
                        "more than one head symbol found on one of the " "virtual tapes"
                    )
                else:
                    heads_found = 0
                    separators_found += 1

        if len(virtual_heads) != separators_found:
            raise tm_exceptions.MalformedExtendedTapeError(
                "there must be 1 virtual head for every tape separator symbol"
            )

        return tuple(virtual_heads)

    def read_input_as_ntm(self, input_str):
        """Simulates the machine as a single-tape Turing machine.
        Yields the configuration at each step."""
        tapes = self._get_tapes_for_input_str(input_str)
        head_symbol = "^"
        tape_separator_symbol = "_"
        extended_tape = ""
        tapes_copy = tapes.copy()
        for tape_copy in tapes_copy:
            tape_str = tape_copy.get_symbols_as_str()
            extended_tape += (
                tape_str[0] + head_symbol + tape_str[1:] + tape_separator_symbol
            )

        current_state = self.initial_state
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
            virtual_heads = self._read_extended_tape(
                extended_tape, head_symbol, tape_separator_symbol
            )
            try:
                next_config = self.transitions[current_state][virtual_heads]
            except KeyError:
                raise exceptions.RejectionException(
                    "the multitape NTM did not reach an accepting " "configuration"
                )
            next_state, moves = next_config[0]
            for move in moves:
                new_head, direction = move
                executing_changes = True

                while executing_changes:
                    if extended_tape[i] == head_symbol:
                        # Head has been found (previous symbol is the head).
                        # This replaces the previous symbol with the new_head.
                        extended_tape = (
                            extended_tape[: i - 1] + new_head + extended_tape[i:]
                        )
                        extended_tape = extended_tape[:i] + "" + extended_tape[i + 1 :]

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
                            extended_tape = (
                                extended_tape[:i]
                                + self.blank_symbol
                                + head_symbol
                                + extended_tape[i:]
                            )

                            i += 1
                        else:
                            extended_tape = (
                                extended_tape[:i] + head_symbol + extended_tape[i:]
                            )

                    elif extended_tape[i] == tape_separator_symbol:
                        executing_changes = False

                    i += 1

            current_state = next_state
            yield {
                TMConfiguration(
                    current_state,
                    TMTape(
                        extended_tape,
                        blank_symbol=self.blank_symbol,
                        current_position=i - 1,
                    ),
                )
            }
