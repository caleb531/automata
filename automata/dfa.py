#!/usr/bin/env python3

import copy
from queue import Queue
import automata.automaton as automaton


class DFA(automaton.Automaton):
    """a deterministic finite automaton"""

    def __init__(self, *, states, symbols, transitions, initial_state,
                 final_states):
        """initializes a complete DFA"""
        self.states = set(states)
        self.symbols = set(symbols)
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.validate_automaton()

    def _validate_transition_symbols(self, start_state, paths):
        """raises an error if the transition symbols are missing or invalid"""

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
        """returns True if this DFA is internally consistent;
        raises the appropriate exception otherwise"""

        self._validate_transition_start_states()

        for start_state, paths in self.transitions.items():

            self._validate_transition_symbols(start_state, paths)

            path_states = set(paths.values())
            self._validate_transition_end_states(path_states)

        self._validate_initial_state()
        self._validate_final_states()

        return True

    def validate_input(self, input_str):
        """returns True if the given string is accepted by this DFA;
        raises the appropriate exception otherwise"""

        current_state = self.initial_state

        for symbol in input_str:
            self._validate_input_symbol(symbol)
            current_state = self.transitions[current_state][symbol]

        if current_state not in self.final_states:
            raise automaton.FinalStateError(
                'the automaton stopped at a non-final state ({})'.format(
                    current_state))

        return current_state

    @classmethod
    def from_nfa(cls, nfa):
        """creates a new DFA that is equivalent to the given NFA"""

        dfa_states = set()
        dfa_symbols = nfa.symbols
        dfa_transitions = {}
        dfa_initial_state = cls._stringify_states({nfa.initial_state})
        dfa_final_states = set()

        queue = Queue()
        queue.put({nfa.initial_state})
        for i in range(0, 2**len(nfa.states)):

            current_states = queue.get()
            current_state_label = cls._stringify_states(current_states)
            dfa_states.add(current_state_label)
            dfa_transitions[current_state_label] = {}

            if (current_states & nfa.final_states):
                dfa_final_states.add(cls._stringify_states(current_states))

            for symbol in nfa.symbols:

                next_current_states = nfa._get_next_current_states(
                    current_states, symbol)
                dfa_transitions[current_state_label][symbol] = (
                    cls._stringify_states(next_current_states))

                queue.put(next_current_states)

        return cls(
            states=dfa_states, symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)
