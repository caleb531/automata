#!/usr/bin/env python3
"""Classes and methods for working with deterministic Turing machines."""

from typing import AbstractSet, Generator, Mapping, Optional, Set, Tuple

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
import automata.tm.tm as tm
from automata.tm.configuration import TMConfiguration
from automata.tm.tape import TMTape

DTMStateT = tm.TMStateT
DTMPathResultT = Tuple[DTMStateT, str, tm.TMDirectionT]
DTMPathT = Mapping[str, DTMPathResultT]
DTMTransitionsT = Mapping[DTMStateT, DTMPathT]


class DTM(tm.TM):
    """A deterministic Turing machine."""

    __slots__ = (
        "states",
        "input_symbols",
        "tape_symbols",
        "transitions",
        "initial_state",
        "blank_symbol",
        "final_states",
    )

    def __init__(
        self,
        *,
        states: AbstractSet[DTMStateT],
        input_symbols: AbstractSet[str],
        tape_symbols: AbstractSet[str],
        transitions: DTMTransitionsT,
        initial_state: DTMStateT,
        blank_symbol: str,
        final_states: AbstractSet[DTMStateT],
    ) -> None:
        """Initialize a complete Turing machine."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            tape_symbols=tape_symbols,
            transitions=transitions,
            initial_state=initial_state,
            blank_symbol=blank_symbol,
            final_states=final_states,
        )

    def _validate_transition_state(self, transition_state: DTMStateT) -> None:
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                "transition state is not valid ({})".format(transition_state)
            )

    def _validate_transition_symbols(
        self, state: DTMStateT, paths: DTMTransitionsT
    ) -> None:
        for tape_symbol in paths.keys():
            if tape_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    "transition symbol {} for state {} is not valid".format(
                        tape_symbol, state
                    )
                )

    def _validate_transition_result_direction(
        self, result_direction: tm.TMDirectionT
    ) -> None:
        if result_direction not in ("L", "N", "R"):
            raise tm_exceptions.InvalidDirectionError(
                "result direction is not valid ({})".format(result_direction)
            )

    def _validate_transition_result(self, result: DTMPathResultT) -> None:
        result_state, result_symbol, result_direction = result
        if result_state not in self.states:
            raise exceptions.InvalidStateError(
                "result state is not valid ({})".format(result_state)
            )
        if result_symbol not in self.tape_symbols:
            raise exceptions.InvalidSymbolError(
                "result symbol is not valid ({})".format(result_symbol)
            )
        self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, paths: DTMPathT) -> None:
        for result in paths.values():
            self._validate_transition_result(result)

    def _validate_transitions(self) -> None:
        for state, paths in self.transitions.items():
            self._validate_transition_state(state)
            self._validate_transition_symbols(state, paths)
            self._validate_transition_results(paths)

    def _validate_final_state_transitions(self) -> None:
        for final_state in self.final_states:
            if final_state in self.transitions:
                raise exceptions.FinalStateError(
                    "final state {} has transitions defined".format(final_state)
                )

    def validate(self) -> bool:
        """Return True if this DTM is internally consistent."""
        self._read_input_symbol_subset()
        self._validate_blank_symbol()
        self._validate_transitions()
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_nonfinal_initial_state()
        self._validate_final_states()
        self._validate_final_state_transitions()
        return True

    def _get_transition(self, state: DTMStateT, tape_symbol: str) -> Optional[DTMPathT]:
        """Get the transiton tuple for the given state and tape symbol."""
        if state in self.transitions and tape_symbol in self.transitions[state]:
            return self.transitions[state][tape_symbol]
        else:
            return None

    def _has_accepted(self, configuration: TMConfiguration) -> bool:
        """Check whether the given config indicates accepted input."""
        return configuration.state in self.final_states

    def _get_next_configuration(self, old_config: TMConfiguration) -> TMConfiguration:
        """Advance to the next configuration."""
        transitions: Set[Optional[DTMPathT]] = {
            self._get_transition(old_config.state, old_config.tape.read_symbol())
        }
        if None in transitions:
            transitions.remove(None)
        if len(transitions) == 0:
            raise exceptions.RejectionException(
                "The machine entered a non-final configuration for which no "
                "transition is defined ({}, {})".format(
                    old_config.state, old_config.tape.read_symbol()
                )
            )
        tape = old_config.tape
        (new_state, new_tape_symbol, direction) = transitions.pop()  # type: ignore
        tape = tape.write_symbol(new_tape_symbol)
        tape = tape.move(direction)
        return TMConfiguration(new_state, tape)

    def read_input_stepwise(
        self, input_str: str
    ) -> Generator[TMConfiguration, None, None]:
        """
        Check if the given string is accepted by this Turing machine.

        Yield the current configuration of the machine at each step.
        """
        current_configuration = TMConfiguration(
            self.initial_state, TMTape(input_str, blank_symbol=self.blank_symbol)
        )
        yield current_configuration

        # The initial state cannot be a final state for a DTM, so the first
        # iteration is always guaranteed to run (as it should)
        while not self._has_accepted(current_configuration):
            current_configuration = self._get_next_configuration(current_configuration)
            yield current_configuration
