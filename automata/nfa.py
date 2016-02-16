#!/usr/bin/env python3

import automata.automaton as automaton


class NFA(automaton.Automaton):
    """a deterministic finite automaton"""

    def validate_automaton(self):
        """returns True if this NFA is internally consistent;
        raises the appropriate exception if this NFA is invalid"""

        for state in self.states:
            if state not in self.transitions:
                raise automaton.MissingStateError(
                    'state {} is missing from transition function'.format(
                        state))

        for start_state, paths in self.transitions.items():

            invalid_states = set().union(*paths.values()).difference(
                self.states)
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

    # TODO
    def validate_input(self, input_str):
        """returns True if the given string is accepted by this NFA;
        raises the appropriate exception if the string is not accepted"""

        return True
