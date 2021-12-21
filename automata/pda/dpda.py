#!/usr/bin/env python3
"""Classes and methods for working with deterministic pushdown automata."""

import copy
from typing import Set, Dict, Tuple, Optional, Generator

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import automata.pda.pda as pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack

DPDAStateT = pda.PDAStateT

DPDASibblingPathT = Dict[str, Tuple[DPDAStateT, str]]
DPDAPathT = Dict[str, DPDASibblingPathT]
DPDATransitionsT = Dict[DPDAStateT, DPDAPathT]

class DPDA(pda.PDA):
    """A deterministic pushdown automaton."""

    transitions : DPDATransitionsT

    def __init__(self,
                 *,
                 states : Set[DPDAStateT],
                 input_symbols : Set[str],
                 stack_symbols : Set[str],
                 transitions : DPDATransitionsT,
                 initial_state : DPDAStateT,
                 initial_stack_symbol : str,
                 final_states : Set[DPDAStateT],
                 acceptance_mode : str = 'both') -> None:
        """Initialize a complete DPDA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.stack_symbols = stack_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states.copy()
        self.acceptance_mode = acceptance_mode
        self.validate()

    def _validate_transition_invalid_symbols(self,
                                             start_state : DPDAStateT,
                                             paths : DPDAPathT) -> None:
        """Raise an error if transition symbols are invalid."""
        for input_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(
                start_state, input_symbol)
            for stack_symbol in symbol_paths:
                self._validate_transition_isolated_lambda_transitions(
                    start_state, input_symbol, stack_symbol)
                self._validate_transition_invalid_stack_symbols(
                    start_state, stack_symbol)

    def _validate_transition_lambda_transition_sibling(self,
                                                       start_state : DPDAStateT,
                                                       sib_path : DPDASibblingPathT) -> None:
        """Check the given sibling path for adjacent lambda transitions."""
        for other_stack_symbol in sib_path:
            if (other_stack_symbol in
                    self.transitions[start_state]['']):
                raise pda_exceptions.NondeterminismError(
                    'A symbol transition is adjacent to a '
                    'lambda transition for this DPDA.')

    def _validate_transition_isolated_lambda_transitions(self,
                                                         start_state : DPDAStateT,
                                                         input_symbol : str,
                                                         stack_symbol : str) -> None:
        """Raise an error if a lambda transition has no sibling transitions."""
        if input_symbol == '':
            sib_transitions = self.transitions[start_state]
            for sib_input_symbol, sib_path in sib_transitions.items():
                if sib_input_symbol != '':
                    self._validate_transition_lambda_transition_sibling(
                        start_state, sib_path)

    def _get_transition(self,
                        state : DPDAStateT,
                        input_symbol : str,
                        stack_symbol : str) -> Optional[Tuple[str, DPDAStateT, str]]:
        """
        Get the transiton tuple for the given state and symbols. Returns None if
        transition lookup fails.
        """
        if (state in self.transitions and
                input_symbol in self.transitions[state] and
                stack_symbol in self.transitions[state][input_symbol]):
            return (
                input_symbol,
            ) + self.transitions[state][input_symbol][stack_symbol]

        return None

    def _check_for_input_rejection(self,
                                   current_configuration : 'PDAConfiguration') -> None:
        """Raise an error if the given config indicates rejected input."""
        if not self._has_accepted(current_configuration):
            raise exceptions.RejectionException(
                'the DPDA stopped in a non-accepting configuration '
                '({state}, {stack})'
                .format(**current_configuration._asdict())
            )

    def _get_next_configuration(self,
                                old_config : 'PDAConfiguration') -> 'PDAConfiguration':
        """Advance to the next configuration."""
        transitions = set()
        if old_config.remaining_input:
            transition_result = self._get_transition(
                old_config.state,
                old_config.remaining_input[0],
                old_config.stack.top()
            )

            if transition_result:
                transitions.add(transition_result)

        transition_result = self._get_transition(
            old_config.state,
            '',
            old_config.stack.top()
        )

        if transition_result:
            transitions.add(transition_result)

        if len(transitions) == 0:
            raise exceptions.RejectionException(
                'The automaton entered a configuration for which no '
                'transition is defined ({}, {}, {})'.format(
                    old_config.state,
                    old_config.remaining_input[0],
                    old_config.stack.top()
                )
            )
        if len(transitions) > 1:
            raise pda_exceptions.NondeterminismError(
                'The automaton entered a configuration for which more'
                'than one transition is defined ({}, {}'.format(
                    old_config.state,
                    old_config.stack.top()
                )
            )
        input_symbol, new_state, new_stack_top = transitions.pop()
        remaining_input = old_config.remaining_input
        if input_symbol:
            remaining_input = remaining_input[1:]
        new_config = PDAConfiguration(
            new_state,
            remaining_input,
            self._replace_stack_top(old_config.stack, new_stack_top)
        )
        return new_config

    def read_input_stepwise(self, input_str : str) -> Generator['PDAConfiguration', None, None]:
        """
        Check if the given string is accepted by this DPDA.

        Yield the DPDA's current configuration at each step.
        """
        current_configuration = PDAConfiguration(
            self.initial_state,
            input_str,
            PDAStack([self.initial_stack_symbol])
        )

        yield current_configuration
        while (
            current_configuration.remaining_input
            or self._has_lambda_transition(
                current_configuration.state,
                current_configuration.stack.top()
            )
        ):
            current_configuration = self._get_next_configuration(
                current_configuration
            )
            yield current_configuration
            if self._has_accepted(current_configuration):
                return
        self._check_for_input_rejection(current_configuration)
