#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""

import copy

import automata.base.exceptions as exceptions
import automata.fa.fa as fa


class NFA(fa.FA):
    """A nondeterministic finite automaton."""

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_states):
        """Initialize a complete NFA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.validate()

    def __add__(self, other):
        """Return the concatenation of this DFA and another DFA."""
        if isinstance(other, NFA):
            return self.concatenate(other)
        else:
            raise NotImplementedError

    def __reversed__(self):
        """Return the reversal of this DFA."""
        return self.reverse()

    @classmethod
    def from_dfa(cls, dfa):
        """Initialize this NFA as one equivalent to the given DFA."""
        nfa_transitions = {}

        for start_state, paths in dfa.transitions.items():
            nfa_transitions[start_state] = {}
            for input_symbol, end_state in paths.items():
                nfa_transitions[start_state][input_symbol] = {end_state}

        return cls(
            states=dfa.states, input_symbols=dfa.input_symbols,
            transitions=nfa_transitions, initial_state=dfa.initial_state,
            final_states=dfa.final_states)

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition symbols are invalid."""
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

    def validate(self):
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
            raise exceptions.RejectionException(
                'the NFA stopped on all non-final states ({})'.format(
                    ', '.join(str(state) for state in current_states)))

    def read_input_stepwise(self, input_str):
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

    def concatenate(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the languages L1 concatenated with L2.
        """
        state_map_a = dict()
        for state in self.states:
            state_map_a[state] = len(state_map_a)

        state_map_b = dict()
        for state in other.states:
            state_map_b[state] = len(state_map_a) + len(state_map_b)

        new_states = set(state_map_a.values()) | set(state_map_b.values())
        new_transitions = dict()
        for state in new_states:
            new_transitions[state] = dict()
        # Transitions of self
        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                new_transitions[state_map_a[state_a]][symbol] = {
                    state_map_a[state_b] for state_b in states
                }

        # Transitions from self to other
        for state in self.final_states:
            if '' not in new_transitions[state_map_a[state]]:
                new_transitions[state_map_a[state]][''] = set()
            new_transitions[state_map_a[state]][''].add(
                state_map_b[other.initial_state]
            )

        # Transitions of other
        for state_a, transitions in other.transitions.items():
            for symbol, states in transitions.items():
                new_transitions[state_map_b[state_a]][symbol] = {
                    state_map_b[state_b] for state_b in states
                }

        # Final states of other
        new_final_states = {state_map_b[state] for state in other.final_states}

        return NFA(
            states=new_states,
            input_symbols=self.input_symbols | other.input_symbols,
            transitions=new_transitions,
            initial_state=state_map_a[self.initial_state],
            final_states=new_final_states
        )

    def kleene_star(self):
        """
        Given an NFA which accepts the language L returns
        an NFA which accepts L repeated 0 or more times.
        """
        new_states = set(self.states)
        new_initial_state = 0
        while new_initial_state in self.states:
            new_initial_state += 1
        new_final_state = new_initial_state + 1
        while new_final_state in self.states:
            new_final_state += 1
        new_states.add(new_initial_state)
        new_states.add(new_final_state)

        # Transitions are the same with a few additions.
        new_transitions = copy.deepcopy(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state and new final state.
        new_transitions[new_initial_state] = {
            '': {self.initial_state, new_final_state}
        }
        # We have no transitions from new final state
        new_transitions[new_final_state] = dict()
        # For each final state in original NFA we add epsilon
        # transition to the old initial state and to the new
        # final state.
        for state in self.final_states:
            if '' not in new_transitions[state]:
                new_transitions[state][''] = set()
            new_transitions[state][''].add(self.initial_state)
            new_transitions[state][''].add(new_final_state)

        return NFA(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states={new_final_state}
        )

    def reverse(self):
        """
        Given an NFA which accepts the language L this function
        returns an NFA which accepts the reverse of L.
        """
        new_states = set(self.states)
        new_initial_state = 0
        while new_initial_state in self.states:
            new_initial_state += 1
        new_states.add(new_initial_state)

        # Transitions are the same except reversed
        new_transitions = dict()
        for state in new_states:
            new_transitions[state] = dict()
        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                for state_b in states:
                    if symbol not in new_transitions[state_b]:
                        new_transitions[state_b][symbol] = set()
                    new_transitions[state_b][symbol].add(state_a)
        new_transitions[new_initial_state][''] = set()
        # And we additionally have epsilon transitions from
        # new initial state to each old final state.
        for state in self.final_states:
            new_transitions[new_initial_state][''].add(state)

        new_final_states = {self.initial_state}

        return NFA(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )
