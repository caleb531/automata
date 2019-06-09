#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic pushdown automata."""

import copy

import automata.base.exceptions as exceptions
import automata.pda.pda as pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack


class NPDA(pda.PDA):
    """A nondeterministic pushdown automaton."""

    def __init__(self, *, states, input_symbols, stack_symbols,
                 transitions, initial_state,
                 initial_stack_symbol, final_states, acceptance_mode='both'):
        """Initialize a complete NPDA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.stack_symbols = stack_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states.copy()
        self.acceptance_mode = acceptance_mode
        self.validate()

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition symbols are invalid."""
        for input_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(
                start_state, input_symbol)
            for stack_symbol in symbol_paths:
                self._validate_transition_invalid_stack_symbols(
                    start_state, stack_symbol)

    def _get_transitions(self, state, input_symbol, stack_symbol):
        """Get the transition tuples for the given state and symbols."""
        transitions = set()
        if (state in self.transitions and
                input_symbol in self.transitions[state] and
                stack_symbol in self.transitions[state][input_symbol]):
            for (
                dest_state,
                new_stack_top
            ) in self.transitions[state][input_symbol][stack_symbol]:
                transitions.add((
                    input_symbol,
                    dest_state,
                    new_stack_top
                ))
        return transitions

    def _get_next_configurations(self, old_config):
        """Advance to the next configurations."""
        transitions = set()
        if old_config.remaining_input:
            transitions.update(self._get_transitions(
                old_config.state,
                old_config.remaining_input[0],
                old_config.stack.top()
            ))
        transitions.update(self._get_transitions(
            old_config.state,
            '',
            old_config.stack.top()
        ))
        new_configs = set()
        for input_symbol, new_state, new_stack_top in transitions:
            remaining_input = old_config.remaining_input
            if input_symbol:
                remaining_input = remaining_input[1:]
            new_config = PDAConfiguration(
                new_state,
                remaining_input,
                self._replace_stack_top(old_config.stack, new_stack_top)
            )
            new_configs.add(new_config)
        return new_configs

    def read_input_stepwise(self, input_str):
        """
        Check if the given string is accepted by this NPDA.

        Yield the NPDA's current configurations at each step.
        """
        current_configurations = set()
        current_configurations.add(PDAConfiguration(
            self.initial_state,
            input_str,
            PDAStack([self.initial_stack_symbol])
        ))

        yield current_configurations

        while current_configurations:
            new_configurations = set()
            for config in current_configurations:
                if self._has_accepted(config):
                    # One accepting configuration is enough.
                    return
                if config.remaining_input:
                    new_configurations.update(
                        self._get_next_configurations(config)
                    )
                elif self._has_lambda_transition(
                    config.state,
                    config.stack.top()
                ):
                    new_configurations.update(
                        self._get_next_configurations(config)
                    )
            current_configurations = new_configurations
            yield current_configurations

        raise exceptions.RejectionException(
            'the NPDA did not reach an accepting configuration'
        )
