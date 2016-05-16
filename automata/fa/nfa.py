#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""

import copy

import automata.fa.fa as fa
import automata.shared.exceptions as exceptions
import automata.fa.dfa


class NFA(fa.FA):
    """A nondeterministic finite automaton."""

    def __init__(self, obj=None, **kwargs):
        """Initialize a complete NFA."""
        if isinstance(obj, automata.fa.dfa.DFA):
            self._init_from_dfa(obj)
        elif isinstance(obj, NFA):
            self._init_from_nfa(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, transitions,
                                 initial_state, final_states):
        """Initialize an NFA from the formal definition parameters."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.validate_self()

    def _init_from_nfa(self, nfa):
        """Initialize this NFA as a deep copy of the given NFA."""
        self.__init__(
            states=nfa.states, input_symbols=nfa.input_symbols,
            transitions=nfa.transitions, initial_state=nfa.initial_state,
            final_states=nfa.final_states)

    def _init_from_dfa(self, dfa):
        """Initialize this NFA as one equivalent to the given DFA."""
        nfa_transitions = {}

        for start_state, paths in dfa.transitions.items():
            nfa_transitions[start_state] = {}
            for input_symbol, end_state in paths.items():
                nfa_transitions[start_state][input_symbol] = {end_state}

        self.__init__(
            states=dfa.states, input_symbols=dfa.input_symbols,
            transitions=nfa_transitions, initial_state=dfa.initial_state,
            final_states=dfa.final_states)

    def _validate_transition_invalid_symbols(self, start_state, paths):
        for input_symbol in paths.keys():
            if input_symbol not in self.input_symbols and input_symbol != '':
                raise exceptions.InvalidSymbolError(
                    'state {} has invalid transition symbol {}'.format(
                        start_state, input_symbol))

    def _validate_transition_end_states(self, start_state, paths):
        """Raise an error if transition end states are invalid."""
        for end_states in paths.values():
            for end_state in end_states:
                if end_state not in self.states:
                    raise exceptions.InvalidStateError(
                        'end state {} for transition on {} is '
                        'not valid'.format(end_state, start_state))

    def validate_self(self):
        """Return True if this NFA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
            self._validate_transition_end_states(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_final_states()
        return True

    def _get_lambda_closure(self, start_state):
        """
        Return the lambda closure for the given state.

        The lambda closure of a state q is the set containing q, along with
        every state that can be reached from q by following only lambda
        transitions.
        """
        stack = []
        encountered_states = set()
        stack.append(start_state)

        while stack:
            state = stack.pop()
            if state not in encountered_states:
                encountered_states.add(state)
                if '' in self.transitions[state]:
                    stack.extend(self.transitions[state][''])

        return encountered_states

    def _get_next_current_states(self, current_states, input_symbol):
        """Return the next set of current states given the current set."""
        next_current_states = set()

        for current_state in current_states:
            symbol_end_states = self.transitions[current_state].get(
                input_symbol)
            if symbol_end_states:
                for end_state in symbol_end_states:
                    next_current_states.update(
                        self._get_lambda_closure(end_state))

        return next_current_states

    def _check_for_input_rejection(self, current_states):
        """Raise an error if the given config indicates rejected input."""
        if not (current_states & self.final_states):
            raise exceptions.RejectionError(
                'the NFA stopped on all non-final states ({})'.format(
                    ', '.join(current_states)))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this NFA.

        Yield the current configuration of the NFA at each step.
        """
        current_states = self._get_lambda_closure(self.initial_state)

        yield current_states
        for input_symbol in input_str:
            current_states = self._get_next_current_states(
                current_states, input_symbol)
            yield current_states

        self._check_for_input_rejection(current_states)
