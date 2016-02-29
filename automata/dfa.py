#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
import itertools
import queue

import automata.automaton as automaton
import automata.nfa


class DFA(automaton.Automaton):
    """A deterministic finite automaton."""

    def __init__(self, obj=None, *, states=None, symbols=None,
                 transitions=None, initial_state=None, final_states=None):
        """Initialize a complete DFA."""
        if isinstance(obj, automata.nfa.NFA):
            self._init_from_nfa(obj)
        elif isinstance(obj, DFA):
            self._init_from_dfa(obj)
        else:
            self.states = states.copy()
            self.symbols = symbols.copy()
            self.transitions = copy.deepcopy(transitions)
            self.initial_state = initial_state
            self.final_states = final_states.copy()
            self.validate_automaton()

    def _validate_transition_symbols(self, start_state, paths):
        """Raise an error if the transition symbols are missing or invalid."""
        path_symbols = set(paths.keys())

        missing_symbols = self.symbols - path_symbols
        if missing_symbols:
            raise automaton.MissingSymbolError(
                'state {} is missing transitions for symbols ({})'.format(
                    start_state, ', '.join(missing_symbols)))

        invalid_symbols = path_symbols - self.symbols
        if invalid_symbols:
            raise automaton.InvalidSymbolError(
                'state {} has invalid transition symbols ({})'.format(
                    start_state, ', '.join(invalid_symbols)))

    def validate_automaton(self):
        """Return True if this DFA is internally consistent."""
        self._validate_transition_start_states()

        for start_state, paths in self.transitions.items():
            self._validate_transition_symbols(start_state, paths)
            path_states = set(paths.values())
            self._validate_transition_end_states(path_states)

        self._validate_initial_state()
        self._validate_final_states()

        return True

    def validate_input(self, input_str):
        """
        Check if the given string is accepted by this DFA.

        Return the state the NFA stopped at if string is valid.
        """
        current_state = self.initial_state

        for symbol in input_str:
            self._validate_input_symbol(symbol)
            current_state = self.transitions[current_state][symbol]

        if current_state not in self.final_states:
            raise automaton.FinalStateError(
                'the automaton stopped at a non-final state ({})'.format(
                    current_state))

        return current_state

    def _init_from_dfa(self, dfa):
        """Initialize this DFA as an exact copy of the given DFA."""
        self.__init__(
            states=dfa.states, symbols=dfa.symbols,
            transitions=dfa.transitions, initial_state=dfa.initial_state,
            final_states=dfa.final_states)

    def _init_from_nfa(self, nfa):
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states = set()
        dfa_symbols = nfa.symbols
        dfa_transitions = {}
        dfa_initial_state = self.__class__._stringify_states(
            (nfa.initial_state,))
        dfa_final_states = set()

        state_queue = queue.Queue()
        state_queue.put({nfa.initial_state})
        max_num_dfa_states = 2**len(nfa.states)
        for i in range(0, max_num_dfa_states):

            current_states = state_queue.get()
            current_state_name = self.__class__._stringify_states(
                current_states)
            dfa_states.add(current_state_name)
            dfa_transitions[current_state_name] = {}

            if (current_states & nfa.final_states):
                dfa_final_states.add(self.__class__._stringify_states(
                    current_states))

            for symbol in nfa.symbols:
                next_current_states = nfa._get_next_current_states(
                    current_states, symbol)
                dfa_transitions[current_state_name][symbol] = (
                    self.__class__._stringify_states(next_current_states))
                state_queue.put(next_current_states)

        self.__init__(
            states=dfa_states, symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)

    def union(self, other):
        """Compute the union of two automata."""
        union_states = set()
        union_symbols = self.symbols
        self._validate_symbol_set_equality(other)
        union_transitions = {}
        union_initial_state = self.__class__._stringify_states(
            (self.initial_state, other.initial_state))
        union_final_states = set()

        state_product = itertools.product(self.states, other.states)
        for self_state, other_state in state_product:

            new_start_state = self.__class__._stringify_states((
                self_state, other_state))
            union_states.add(new_start_state)
            union_transitions[new_start_state] = {}

            if (self_state in self.final_states or other_state in
                    other.final_states):
                union_final_states.add(new_start_state)

            for symbol in union_symbols:
                new_end_state = self.__class__._stringify_states((
                    self.transitions[self_state][symbol],
                    other.transitions[other_state][symbol]))
                union_transitions[new_start_state][symbol] = (
                    new_end_state)

        return DFA(
            states=union_states, symbols=union_symbols,
            transitions=union_transitions, initial_state=union_initial_state,
            final_states=union_final_states)

    def __or__(self, other):
        """Compute the union of two automata via the | operator."""
        return self.union(other)

    def intersection(self, other):
        """Compute the intersection of two automata."""
        intersection = self | other
        intersection.final_states = set()
        final_state_product = itertools.product(
            self.final_states, other.final_states)
        for self_final_state, other_final_state in final_state_product:
            intersection.final_states.add(self.__class__._stringify_states((
                self_final_state, other_final_state)))
        return intersection

    def __and__(self, other):
        """Compute the intersection of two automata via the & operator."""
        return self.intersection(other)
