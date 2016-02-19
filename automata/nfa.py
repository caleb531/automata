#!/usr/bin/env python3

import automata.automaton as automaton


class NFA(automaton.Automaton):
    """a nondeterministic finite automaton"""

    def __init__(self, states, symbols, transitions, initial_state,
                 final_states):
        """initializes a complete NFA"""
        self.states = set(states)
        self.symbols = set(symbols)
        self.transitions = NFA.clone_transitions(transitions)
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.validate_automaton()

    @staticmethod
    def clone_transitions(transitions):
        """clones the given transitions dictionary"""

        cloned_transitions = {}
        for start_state, paths in transitions.items():

            cloned_transitions[start_state] = {}
            for symbol, end_states in paths.items():
                cloned_transitions[start_state][symbol] = set(
                    transitions[start_state][symbol])

        return cloned_transitions

    def validate_transition_symbols(self, start_state, paths):
        """raises an error if the transition symbols are missing or invalid"""

        path_symbols = set(paths.keys())
        invalid_symbols = path_symbols - self.symbols.union({''})
        if invalid_symbols:
            raise automaton.InvalidSymbolError(
                'symbols are not valid ({})'.format(
                    ', '.join(invalid_symbols)))

    def validate_automaton(self):
        """returns True if this NFA is internally consistent;
        raises the appropriate exception otherwise"""

        self.validate_transition_start_states()

        for start_state, paths in self.transitions.items():

            self.validate_transition_symbols(start_state, paths)

            path_states = set().union(*paths.values())
            self.validate_transition_end_states(path_states)

        self.validate_initial_state()
        self.validate_final_states()

        return True

    def get_next_nfa_current_states(self, current_states, symbol=None):
        """returns the next set of current states given the current set;
        used when validating input for this NFA"""

        next_current_states = set()
        for current_state in current_states:

            symbol_end_states = self.transitions[current_state].get(symbol)
            empty_str_end_states = self.transitions[current_state].get('')

            if symbol_end_states:
                next_current_states.update(symbol_end_states)

            if empty_str_end_states:
                next_current_states.update(empty_str_end_states)

            if not symbol_end_states and not empty_str_end_states:
                next_current_states.add(current_state)

        return next_current_states

    def get_next_dfa_current_states(self, current_states, symbol=None):
        """returns the next set of current states given the current set;
        used when converting this NFA to a DFA (see DFA.from_nfa)"""

        next_current_states = set()
        for current_state in current_states:

            if symbol in self.transitions[current_state]:
                next_current_states.update(
                    self.transitions[current_state][symbol])

        return next_current_states

    def validate_input(self, input_str):
        """returns True if the given string is accepted by this NFA;
        raises the appropriate exception otherwise"""

        current_states = {self.initial_state}

        for symbol in input_str:

            self.validate_input_symbol(symbol)
            current_states = self.get_next_nfa_current_states(
                current_states, symbol)

        current_states = self.get_next_nfa_current_states(current_states)

        if not (current_states & self.final_states):
            raise automaton.FinalStateError(
                'the automaton stopped on all non-final states ({})'.format(
                    (current_states - self.final_states)))

        return current_states
