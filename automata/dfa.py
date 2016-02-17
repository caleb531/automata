#!/usr/bin/env python3

import json
import automata.automaton as automaton


class DFA(automaton.Automaton):
    """a deterministic finite automaton"""

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
    def from_json(json_str):
        """constructs a new DFA from the given JSON string"""

        dfa_dict = json.loads(json_str)

        dfa_dict['states'] = set(dfa_dict['states'])
        dfa_dict['symbols'] = set(dfa_dict['symbols'])
        dfa_dict['final_states'] = set(dfa_dict['final_states'])

        return DFA(**dfa_dict)
