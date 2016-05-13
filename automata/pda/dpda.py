#!/usr/bin/env python3
"""Classes and methods for working with deterministic pushdown automata."""

import copy

import automata.pda.pda as pda
import automata.shared.exceptions as exceptions


class DPDA(pda.PDA):
    """A deterministic pushdown automaton."""

    def __init__(self, obj=None, **kwargs):
        """Initialize a complete DPDA."""
        if isinstance(obj, DPDA):
            self._init_from_dpda(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_dpda(self, dpda):
        """Initialize this DPDA as an exact copy of the given DPDA."""
        self.__init__(
            states=dpda.states, input_symbols=dpda.input_symbols,
            stack_symbols=dpda.stack_symbols, transitions=dpda.transitions,
            initial_state=dpda.initial_state,
            initial_stack_symbol=dpda.initial_stack_symbol,
            final_states=dpda.final_states)

    def _init_from_formal_params(self, *, states, input_symbols, stack_symbols,
                                 transitions, initial_state,
                                 initial_stack_symbol, final_states):
        """Initialize a DPDA from the formal definition parameters."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.stack_symbols = stack_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states.copy()
        self.validate_self()

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition symbols are invalid."""
        for path_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(
                start_state, path_symbol)
            self._validate_transition_invalid_stack_symbols(
                start_state, symbol_paths)

    def _validate_transition_invalid_input_symbols(self, start_state,
                                                   path_symbol):
        """Raise an error if transition input symbols are invalid."""
        if path_symbol not in self.input_symbols and path_symbol != '':
            raise exceptions.InvalidSymbolError(
                'state {} has invalid transition input symbol {}'.format(
                    start_state, path_symbol))

    def _validate_transition_invalid_stack_symbols(self, start_state, paths):
        """Raise an error if transition stack symbols are invalid."""
        for path_symbol in paths.keys():
            if path_symbol not in self.stack_symbols:
                raise exceptions.InvalidSymbolError(
                    'state {} has invalid transition stack symbol {}'.format(
                        start_state, path_symbol))

    def _validate_initial_stack_symbol(self):
        """Raise an error if initial stack symbol is invalid."""
        if self.initial_stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                'initial stack symbol {} is invalid'.format(
                    self.initial_stack_symbol))

    def validate_self(self):
        """Return True if this DPDA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_stack_symbol()
        self._validate_final_states()
        return True

    def _has_lambda_transition(self, state, stack_symbol):
        """Return True if the current config has any lambda transitions."""
        return (state in self.transitions and
                '' in self.transitions[state] and
                stack_symbol in self.transitions[state][''])

    def _get_transition(self, state, input_symbol, stack_symbol):
        """Get the transiton tuple for the given state and symbols."""
        if (state in self.transitions and
                input_symbol in self.transitions[state] and
                stack_symbol in self.transitions[state][input_symbol]):
            return self.transitions[state][input_symbol][stack_symbol]
        else:
            raise exceptions.RejectionError(
                'The automaton entered a configuration for which no '
                'transition is defined ({}, {}, {})'.format(
                    state, input_symbol, stack_symbol))

    def _replace_stack_top(self, stack, new_stack_top):
        stack.pop()
        if new_stack_top != '':
            stack.extend(reversed(new_stack_top))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this DPDA.

        Yield the DPDA's current state and current stack at each step.
        """
        current_state = self.initial_state
        stack = [self.initial_stack_symbol]

        yield current_state, stack
        for input_symbol in input_str:
            current_state, new_stack_top = self._get_transition(
                current_state, input_symbol, stack[-1])
            self._replace_stack_top(stack, new_stack_top)
            # Follow any lambda transitions from the current configuration
            if self._has_lambda_transition(current_state, stack[-1]):
                current_state, new_stack_top = (
                    self._get_transition(current_state, '', stack[-1]))
                self._replace_stack_top(stack, new_stack_top)
            yield current_state, stack

        # If current state is not a final state and stack is not empty
        if current_state not in self.final_states and stack:
            raise exceptions.RejectionError(
                'the DPDA stopped in a non-accepting configuration '
                '({}, {})'.format(current_state, stack))
