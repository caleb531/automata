#!/usr/bin/env python3
"""Classes and methods for working with all pushdown automata."""

import abc
from typing import AbstractSet, Literal

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
from automata.base.automaton import Automaton, AutomatonStateT, AutomatonTransitionsT
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack

PDAStateT = AutomatonStateT
PDATransitionsT = AutomatonTransitionsT
PDAAcceptanceModeT = Literal["final_state", "empty_stack", "both"]


class PDA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for pushdown automata."""

    __slots__ = tuple()

    stack_symbols: AbstractSet[str]
    initial_stack_symbol: str
    acceptance_mode: PDAAcceptanceModeT

    def _validate_transition_invalid_input_symbols(
        self, start_state: PDAStateT, input_symbol: str
    ) -> None:
        """Raise an error if transition input symbols are invalid."""
        if input_symbol not in self.input_symbols and input_symbol != "":
            raise exceptions.InvalidSymbolError(
                "state {} has invalid transition input symbol {}".format(
                    start_state, input_symbol
                )
            )

    def _validate_transition_invalid_stack_symbols(
        self, start_state: PDAStateT, stack_symbol: str
    ) -> None:
        """Raise an error if transition stack symbols are invalid."""
        if stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                "state {} has invalid transition stack symbol {}".format(
                    start_state, stack_symbol
                )
            )

    def _validate_initial_stack_symbol(self) -> None:
        """Raise an error if initial stack symbol is invalid."""
        if self.initial_stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                "initial stack symbol {} is invalid".format(self.initial_stack_symbol)
            )

    def _validate_acceptance(self) -> None:
        """Raise an error if the acceptance mode is invalid."""
        if self.acceptance_mode not in ("final_state", "empty_stack", "both"):
            raise pda_exceptions.InvalidAcceptanceModeError(
                "acceptance mode {} is invalid".format(self.acceptance_mode)
            )

    @abc.abstractmethod
    def _validate_transition_invalid_symbols(
        self, start_state: PDAStateT, paths: PDATransitionsT
    ) -> None:
        pass

    def validate(self) -> None:
        """Return True if this PDA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_stack_symbol()
        self._validate_final_states()
        self._validate_acceptance()

    def _has_lambda_transition(self, state: PDAStateT, stack_symbol: str) -> bool:
        """Return True if the current config has any lambda transitions."""
        return (
            state in self.transitions
            and "" in self.transitions[state]
            and stack_symbol in self.transitions[state][""]
        )

    def _replace_stack_top(self, stack: PDAStack, new_stack_top: str) -> PDAStack:
        """Replace the top of the PDA stack with another symbol"""
        if new_stack_top == "":
            new_stack = stack.pop()
        else:
            new_stack = stack.replace(new_stack_top)
        return new_stack

    def _has_accepted(self, current_configuration: PDAConfiguration) -> bool:
        """Check whether the given config indicates accepted input."""
        # If there's input left, we're not finished.
        if current_configuration.remaining_input:
            return False
        if self.acceptance_mode in ("empty_stack", "both"):
            # If the stack is empty, we accept.
            if not current_configuration.stack:
                return True
        if self.acceptance_mode in ("final_state", "both"):
            # If current state is a final state, we accept.
            if current_configuration.state in self.final_states:
                return True
        # Otherwise, not.
        return False
