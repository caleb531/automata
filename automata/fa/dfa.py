#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
import queue

import automata.fa.fa as fa
import automata.base.exceptions as exceptions
import automata.fa.nfa


class DFA(fa.FA):
    """A deterministic finite automaton."""

    def __init__(self, obj=None, **kwargs):
        """Initialize a complete DFA."""
        if isinstance(obj, automata.fa.nfa.NFA):
            self._init_from_nfa(obj)
        elif isinstance(obj, DFA):
            self._init_from_dfa(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, transitions,
                                 initial_state, final_states):
        """Initialize a DFA from the formal definition parameters."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.validate_self()

    def _validate_transition_missing_symbols(self, start_state, paths):
        """Raise an error if the transition input_symbols are missing."""
        for input_symbol in self.input_symbols:
            if input_symbol not in paths:
                raise exceptions.MissingSymbolError(
                    'state {} is missing transitions for symbol {}'.format(
                        start_state, input_symbol))

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition input symbols are invalid."""
        for input_symbol in paths.keys():
            if input_symbol not in self.input_symbols:
                raise exceptions.InvalidSymbolError(
                    'state {} has invalid transition symbol {}'.format(
                        start_state, input_symbol))

    def _validate_transition_start_states(self):
        """Raise an error if transition start states are missing."""
        for state in self.states:
            if state not in self.transitions:
                raise exceptions.MissingStateError(
                    'transition start state {} is missing'.format(
                        state))

    def _validate_transition_end_states(self, start_state, paths):
        """Raise an error if transition end states are invalid."""
        for end_state in paths.values():
            if end_state not in self.states:
                raise exceptions.InvalidStateError(
                    'end state {} for transition on {} is not valid'.format(
                        end_state, start_state))

    def _validate_transitions(self, start_state, paths):
        """Raise an error if transitions are missing or invalid."""
        self._validate_transition_missing_symbols(start_state, paths)
        self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_transition_end_states(start_state, paths)

    def validate_self(self):
        """Return True if this DFA is internally consistent."""
        self._validate_transition_start_states()
        for start_state, paths in self.transitions.items():
            self._validate_transitions(start_state, paths)
        self._validate_initial_state()
        self._validate_final_states()
        return True

    def _get_next_current_state(self, current_state, input_symbol):
        """
        Follow the transition for the given input symbol on the current state.

        Raise an error if the transition does not exist.
        """
        if input_symbol in self.transitions[current_state]:
            return self.transitions[current_state][input_symbol]
        else:
            raise exceptions.RejectionError(
                '{} is not a valid input symbol'.format(input_symbol))

    def _check_for_input_rejection(self, current_state):
        """Raise an error if the given config indicates rejected input."""
        if current_state not in self.final_states:
            raise exceptions.RejectionError(
                'the DFA stopped on a non-final state ({})'.format(
                    current_state))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this DFA.

        Yield the current configuration of the DFA at each step.
        """
        current_state = self.initial_state

        yield current_state
        for input_symbol in input_str:
            current_state = self._get_next_current_state(
                current_state, input_symbol)
            yield current_state

        self._check_for_input_rejection(current_state)

    def _init_from_dfa(self, dfa):
        """Initialize this DFA as a deep copy of the given DFA."""
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

            for input_symbol in nfa.input_symbols:
                next_current_states = nfa._get_next_current_states(
                    current_states, input_symbol)
                dfa_transitions[current_state_name][input_symbol] = (
                    self.__class__._stringify_states(next_current_states))
                state_queue.put(next_current_states)

        self.__init__(
            states=dfa_states, input_symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)
