#!/usr/bin/env python3

import copy
from queue import Queue
import automata.automaton as automaton


class DFA(automaton.Automaton):
    """a deterministic finite automaton"""

    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """initializes a complete DFA"""
        self.states = set(states)
        self.symbols = set(symbols)
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.validate_automaton()

    def validate_automaton(self):
        """returns True if this DFA is internally consistent;
        raises the appropriate exception otherwise"""

        for state in self.states:
            if state not in self.transitions:
                raise automaton.MissingStateError(
                    'state {} is missing from transition function'.format(
                        state))

        for start_state, paths in self.transitions.items():

            path_symbols = set(paths.keys())
            missing_symbols = self.symbols - path_symbols
            if missing_symbols:
                raise automaton.MissingSymbolError(
                    'state {} is missing transitions for symbols ({})'.format(
                        start_state, ', '.join(missing_symbols)))

            invalid_symbols = path_symbols - self.symbols
            if invalid_symbols:
                raise automaton.InvalidSymbolError(
                    'symbols are not valid ({})'.format(
                        ', '.join(invalid_symbols)))

            path_states = set(paths.values())
            invalid_states = path_states - self.states
            if invalid_states:
                raise automaton.InvalidStateError(
                    'states are not valid ({})'.format(
                        ', '.join(invalid_states)))

        if self.initial_state not in self.states:
            raise automaton.InvalidStateError(
                '{} is not a valid state'.format(self.initial_state))

        invalid_final_states = self.final_states - self.states
        if invalid_final_states:
            raise automaton.InvalidStateError(
                'states are not valid ({})'.format(
                    ', '.join(invalid_final_states)))

        return True

    def validate_input(self, input_str):
        """returns True if the given string is accepted by this DFA;
        raises the appropriate exception otherwise"""

        current_state = self.initial_state

        for symbol in input_str:
            if symbol not in self.symbols:
                raise automaton.InvalidSymbolError(
                    '{} is not a valid symbol'.format(symbol))
            current_state = self.transitions[current_state][symbol]

        if current_state not in self.final_states:
            raise automaton.FinalStateError(
                'the automaton stopped on a non-final state')

        return current_state

    @staticmethod
    def from_nfa(nfa):
        """converts the given NFA to a DFA"""

        queue = Queue()
        queue.put({nfa.initial_state})
        dfa_states = set()
        dfa_symbols = nfa.symbols
        dfa_transitions = {}
        dfa_initial_state = '{{{}}}'.format(nfa.initial_state)
        dfa_final_states = set()

        for i in range(0, 2**len(nfa.states)):

            current_states = queue.get()
            current_state_str = DFA.stringify_states(current_states)
            dfa_states.add(current_state_str)
            dfa_transitions[current_state_str] = {}

            if (current_states & nfa.final_states):
                dfa_final_states.add(DFA.stringify_states(current_states))

            for symbol in nfa.symbols:

                new_current_states = set()
                for sub_state in current_states:
                    if symbol in nfa.transitions[sub_state]:
                        new_current_states.update(
                            nfa.transitions[sub_state][symbol])

                dfa_transitions[current_state_str][symbol] = \
                    DFA.stringify_states(new_current_states)

                queue.put(new_current_states)

        return DFA(
            states=dfa_states, symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)
