#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc

import automata.base.exceptions as exceptions
from automata.base.automaton import Automaton


class TM(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for Turing machines."""

    def _read_input_symbol_subset(self):
        if not (self.input_symbols < self.tape_symbols):
            raise exceptions.MissingSymbolError(
                'The set of tape symbols is missing symbols from the input '
                'symbol set ({})'.format(
                    self.tape_symbols - self.input_symbols))


    def _validate_blank_symbol(self):
        """Raise an error if blank symbol is not a tape symbol."""
        if self.blank_symbol not in self.tape_symbols:
            raise exceptions.InvalidSymbolError(
                'blank symbol {} is not a tape symbol'.format(
                    self.blank_symbol))

    def _validate_nonfinal_initial_state(self):
        """Raise an error if the initial state is a final state."""
        if self.initial_state in self.final_states:
            raise exceptions.InitialStateError(
                'initial state {} cannot be a final state'.format(
                    self.initial_state))
