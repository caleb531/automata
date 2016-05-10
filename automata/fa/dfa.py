#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
import queue

import automata.fa.fa as fa
import automata.shared.exceptions as exceptions
import automata.fa.nfa


class DFA(fa.FA):
    """A deterministic finite automaton."""

    def __init__(self, obj=None, *, states=None, input_symbols=None,
                 transitions=None, initial_state=None, final_states=None):
        """Initialize a complete DFA."""
        if isinstance(obj, automata.fa.nfa.NFA):
            self._init_from_nfa(obj)
        elif isinstance(obj, DFA):
            self._init_from_dfa(obj)
        else:
            self.states = states.copy()
            self.input_symbols = input_symbols.copy()
            self.transitions = copy.deepcopy(transitions)
            self.initial_state = initial_state
            self.final_states = final_states.copy()
            self.validate_self()

    def _validate_transition_symbols(self, start_state, paths):
        """Raise an error if the transition symbols are missing or invalid."""
        path_symbols = set(paths.keys())

        missing_symbols = self.input_symbols - path_symbols
        if missing_symbols:
            raise exceptions.MissingSymbolError(
                'state {} is missing transitions for symbols ({})'.format(
                    start_state, ', '.join(missing_symbols)))

        invalid_symbols = path_symbols - self.input_symbols
        if invalid_symbols:
            raise exceptions.InvalidSymbolError(
                'state {} has invalid transition symbols ({})'.format(
                    start_state, ', '.join(invalid_symbols)))

    def validate_self(self):
        """Return True if this DFA is internally consistent."""
        self._validate_transition_start_states()

        for start_state, paths in self.transitions.items():
            self._validate_transition_symbols(start_state, paths)
            path_states = set(paths.values())
            self._validate_transition_end_states(path_states)

        self._validate_initial_state()
        self._validate_final_states()

        return True

    def _validate_input_symbol(self, symbol):
        """Raise an error if the given input symbol is invalid."""
        if symbol not in self.input_symbols:
            raise exceptions.RejectionError(
                '{} is not a valid input symbol'.format(symbol))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this DFA.

        Yield the current configuration of the FA at each step.
        """
        current_state = self.initial_state

        yield current_state
        for symbol in input_str:
            self._validate_input_symbol(symbol)
            current_state = self.transitions[current_state][symbol]
            yield current_state

        if current_state not in self.final_states:
            raise exceptions.RejectionError(
                'the FA stopped on a non-final state ({})'.format(
                    current_state))

    def _validate_input_return(self, input_str):
        """
        Check if the given string is accepted by this DFA.

        Return the state the machine stopped on if the string is valid.
        """
        validation_generator = self._validate_input_yield(input_str)
        for current_state in validation_generator:
            pass
        return current_state

    def validate_input(self, input_str, step=False):
        """
        Check if the given string is accepted by this DFA.

        If step is True, yield the configuration at each step. Otherwise,
        return the final configuration.
        """
        if step:
            return self._validate_input_yield(input_str)
        else:
            return self._validate_input_return(input_str)

    def _init_from_dfa(self, dfa):
        """Initialize this DFA as an exact copy of the given DFA."""
        self.__init__(
            states=dfa.states, input_symbols=dfa.input_symbols,
            transitions=dfa.transitions, initial_state=dfa.initial_state,
            final_states=dfa.final_states)

    @staticmethod
    def _stringify_states(states):
        if isinstance(states, set):
            states = sorted(states)
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(','.join(states))

    def _init_from_nfa(self, nfa):
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states = set()
        dfa_symbols = nfa.input_symbols
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

            for symbol in nfa.input_symbols:
                next_current_states = nfa._get_next_current_states(
                    current_states, symbol)
                dfa_transitions[current_state_name][symbol] = (
                    self.__class__._stringify_states(next_current_states))
                state_queue.put(next_current_states)

        self.__init__(
            states=dfa_states, input_symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)
