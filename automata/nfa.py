#!/usr/bin/env python3

import automata.automaton as automaton


class NFA(automaton.Automaton):
    """a nondeterministic finite automaton"""

    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """initializes a complete NFA"""
        self.states = set(states)
        self.symbols = set(symbols)
        self.transitions = {}
        for start_state, paths in transitions.items():
            self.transitions[start_state] = {}
            for symbol, end_states in paths.items():
                self.transitions[start_state][symbol] = set(
                    transitions[start_state][symbol])
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.validate_automaton()

    def validate_automaton(self):
        """returns True if this NFA is internally consistent;
        raises the appropriate exception otherwise"""

        self.validate_transition_start_states()

        for start_state, paths in self.transitions.items():

            path_symbols = set(paths.keys())
            invalid_symbols = path_symbols - self.symbols.union({''})
            if invalid_symbols:
                raise automaton.InvalidSymbolError(
                    'symbols are not valid ({})'.format(
                        ', '.join(invalid_symbols)))

            path_states = set().union(*paths.values())
            self.validate_transition_end_states(path_states)

        self.validate_initial_state()
        self.validate_final_states()

        return True

    def validate_input(self, input_str):
        """returns True if the given string is accepted by this NFA;
        raises the appropriate exception otherwise"""

        current_states = {self.initial_state}

        for symbol in input_str:

            if symbol not in self.symbols:
                raise automaton.InvalidSymbolError(
                    '{} is not a valid symbol'.format(symbol))

            new_current_states = set()
            for current_state in current_states:

                symbol_transition = symbol in self.transitions[current_state]
                empty_str_transition = '' in self.transitions[current_state]

                if symbol_transition:
                    for end_state in self.transitions[current_state][symbol]:
                        new_current_states.add(end_state)

                if empty_str_transition:
                    for end_state in self.transitions[current_state]['']:
                        new_current_states.add(end_state)

                if not symbol_transition and not empty_str_transition:
                    new_current_states.add(current_state)

            current_states = new_current_states

        new_current_states = set()
        for current_state in current_states:
            if '' in self.transitions[current_state]:
                for end_state in self.transitions[current_state]['']:
                    new_current_states.add(end_state)
            else:
                new_current_states.add(current_state)
        current_states = new_current_states

        if not (current_states & self.final_states):
            raise automaton.FinalStateError(
                'the automaton stopped on all non-final states ({})'.format(
                    (current_states - self.final_states)))

        return current_states
