#!/usr/bin/env python3
"""Classes and methods for working with deterministic pushdown automata."""

import copy

import automata.pda.pda as pda


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
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states.copy()
        self.validate_self()
