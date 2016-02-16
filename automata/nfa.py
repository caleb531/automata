#!/usr/bin/env python3

import automata.automaton as automaton


class NFA(automaton.Automaton):
    """a nondeterministic finite automaton"""

    def validate_automaton(self):
        """returns True if this NFA is internally consistent;
        raises the appropriate exception if this NFA is invalid"""

        for state in self.states:
            if state not in self.transitions:
                raise automaton.MissingStateError(
                    'state {} is missing from transition function'.format(
                        state))

        for start_state, paths in self.transitions.items():

            path_symbols = set(paths.keys())
            invalid_symbols = path_symbols - self.symbols.union({''})
            if invalid_symbols:
                raise automaton.InvalidSymbolError(
                    'symbols are not valid ({})'.format(
                        ', '.join(invalid_symbols)))

            path_states = set().union(*paths.values())
            invalid_states = path_states - self.states
            if invalid_states:
                raise automaton.InvalidStateError(
                    'states are not valid ({})'.format(
                        ', '.join(invalid_states)))

        if self.initial_state not in self.states:
            raise automaton.InvalidStateError(
                '{} is not a valid state'.format(self.initial_state))

        for state in self.final_states:
            if state not in self.states:
                raise automaton.InvalidStateError(
                    '{} is not a valid state'.format(state))

        return True

    def validate_input(self, input_str):
        """returns True if the given string is accepted by this NFA;
        raises the appropriate exception if the string is not accepted"""

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
