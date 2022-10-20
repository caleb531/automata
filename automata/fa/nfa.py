#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""

import copy

import networkx as nx
from pydot import Dot, Edge, Node

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.regex.parser import parse_regex


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
        self.recompute_lambda_closures()
        self.validate()

    def recompute_lambda_closures(self):
        """
        Computes a dictionary of the lambda closures for this NFA, where each
        key is the state name and the value is the lambda closure for that
        corresponding state. This dictionary is cached for the lifetime of the
        instance when the NFA is initialized, and can be recomputed by simply
        calling this method again.

        The lambda closure of a state q is the set containing q, along with
        every state that can be reached from q by following only lambda
        transitions.
        """
        lambda_graph = nx.DiGraph()
        lambda_graph.add_nodes_from(self.states)
        lambda_graph.add_edges_from([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for char, end_states in transition.items()
            for end_state in end_states
            if char == ''
        ])

        self.lambda_closures = {
            state: nx.descendants(lambda_graph, state) | {state}
            for state in self.states
        }

    def copy(self):
        """
        Create a deep copy of the NFA. Overrides copy in base class due to
        extra lambda_closures parameter (which is cached on the instance
        but should not be passed to the initializer).
        """
        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.final_states
        )

    def __add__(self, other):
        """Return the concatenation of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.concatenate(other)
        else:
            raise NotImplementedError

    def __or__(self, other):
        """Return the union of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.union(other)
        else:
            raise NotImplementedError

    def __reversed__(self):
        """Return the reversal of this DFA."""
        return self.reverse()

    @classmethod
    def from_dfa(cls, dfa):
        """Initialize this NFA as one equivalent to the given DFA."""
        nfa_transitions = {
            start_state: {
                input_symbol: {end_state}
                for input_symbol, end_state in paths.items()
            }
            for start_state, paths in dfa.transitions.items()
        }

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

    @classmethod
    def _from_symbol(cls, symbol, input_symbols=None):
        """Generate NFA from single symbol, `input symbols` may be passed to initialize input_symbols for NFA"""
        states = {0, 1}
        initial_state = 0
        if input_symbols is None:
            input_symbols = {symbol}
        transitions = {0: {symbol: {1}}}
        final_states = {1}

        return cls(
            states=states,
            input_symbols=input_symbols,
            initial_state=initial_state,
            transitions=transitions,
            final_states=final_states
        )

    @classmethod
    def from_regex(cls, regex):
        """Initialize this NFA as one equivalent to the given regular expression"""
        input_symbols = set(regex) - {'*', '|', '(', ')', '?'}
        nfa_builder = parse_regex(regex)

        return cls(
            states=set(nfa_builder._transitions.keys()),
            input_symbols=input_symbols,
            transitions=nfa_builder._transitions,
            initial_state=nfa_builder._initial_state,
            final_states=nfa_builder._final_states
        )

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

    def _get_next_current_states(self, current_states, input_symbol):
        """Return the next set of current states given the current set."""
        next_current_states = set()

        for current_state in current_states:
            if current_state not in self.transitions:
                continue
            current_transition = self.transitions[current_state]
            for end_state in current_transition.get(input_symbol, {}):
                next_current_states.update(
                    self.lambda_closures[end_state])

        return next_current_states

    def _remove_unreachable_states(self):
        """Remove states which are not reachable from the initial state."""
        reachable_states = self._compute_reachable_states()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transitions[state]
            if state in self.final_states:
                self.final_states.remove(state)

    def _compute_reachable_states(self):
        """Compute the states which are reachable from the initial state."""
        graph = nx.DiGraph([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for end_states in transition.values()
            for end_state in end_states
        ])
        graph.add_nodes_from(self.states)

        return nx.descendants(graph, self.initial_state) | {self.initial_state}

    def _remove_empty_transitions(self):
        """Deletes transitions to empty set of states"""
        to_delete_sym = {}
        for state in self.transitions.keys():
            for input_symbol, to_states in self.transitions[state].items():
                if to_states == set():
                    if state in to_delete_sym:
                        to_delete_sym[state].add(input_symbol)
                    else:
                        to_delete_sym[state] = {input_symbol}

        for state, input_symbols in to_delete_sym.items():
            for input_symbol in input_symbols:
                del self.transitions[state][input_symbol]

        for state in list(self.transitions.keys()):
            if self.transitions[state] == dict():
                del self.transitions[state]

    def eliminate_lambda(self):
        """Removes epsilon transitions from the NFA which recognizes the same language."""
        for state in self.states:
            lambda_enclosure = self.lambda_closures[state] - {state}
            for input_symbol in self.input_symbols:
                self.transitions[state] = {
                    **self.transitions.get(state, {}),
                    input_symbol: {
                        *(self.transitions
                            .get(state, {})
                            .get(input_symbol, set())),
                        *self._get_next_current_states(
                            lambda_enclosure, input_symbol)
                    }
                }

            if (self.final_states & lambda_enclosure):
                self.final_states.add(state)
            self.transitions[state].pop('', None)

        self._remove_unreachable_states()
        self._remove_empty_transitions()
        self.recompute_lambda_closures()

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
        current_states = self.lambda_closures[self.initial_state]

        yield current_states
        for input_symbol in input_str:
            current_states = self._get_next_current_states(
                current_states, input_symbol)
            yield current_states

        self._check_for_input_rejection(current_states)

    @staticmethod
    def _get_state_maps(state_set_a, state_set_b, *, start=0):
        """
        Generate state map dicts from given sets. Useful when the state set has
        to be a union of the state sets of component FAs.
        """

        state_map_a = {
            state: i
            for i, state in enumerate(state_set_a, start=start)
        }

        state_map_b = {
            state: i
            for i, state in enumerate(state_set_b, start=max(state_map_a.values())+1)
        }

        return (state_map_a, state_map_b)

    def union(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the union of L1 and L2.
        """
        if not isinstance(other, NFA):
            raise NotImplementedError

        # Starting at 1 because 0 is for the initial state
        (state_map_a, state_map_b) = NFA._get_state_maps(self.states, other.states, start=1)

        new_states = set(state_map_a.values()) | set(state_map_b.values()) | {0}
        new_transitions = {state: dict() for state in new_states}

        # Connect new initial state to both branch
        new_transitions[0] = {'': {state_map_a[self.initial_state], state_map_b[other.initial_state]}}

        # Transitions of self
        NFA._load_new_transition_dict(state_map_a, self.transitions, new_transitions)
        # Transitions of other
        NFA._load_new_transition_dict(state_map_b, other.transitions, new_transitions)

        # Final states
        new_final_states = (
            {state_map_a[state] for state in self.final_states}
            | {state_map_b[state] for state in other.final_states}
        )

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols | other.input_symbols,
            transitions=new_transitions,
            initial_state=0,
            final_states=new_final_states
        )

    def concatenate(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the languages L1 concatenated with L2.
        """

        (state_map_a, state_map_b) = NFA._get_state_maps(self.states, other.states)

        new_states = set(state_map_a.values()) | set(state_map_b.values())
        new_transitions = {state: dict() for state in new_states}

        # Transitions of self
        NFA._load_new_transition_dict(state_map_a, self.transitions, new_transitions)
        # Transitions of other
        NFA._load_new_transition_dict(state_map_b, other.transitions, new_transitions)

        # Transitions from self to other
        for state in self.final_states:
            new_transitions[state_map_a[state]].setdefault('', set()).add(
                state_map_b[other.initial_state]
            )

        # Final states of other
        new_final_states = {state_map_b[state] for state in other.final_states}

        return self.__class__(
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
        new_initial_state = NFA._add_new_state(new_states)

        # Transitions are the same with a few additions.
        new_transitions = copy.deepcopy(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {
            '': {self.initial_state}
        }
        # For each final state in original NFA we add epsilon
        # transition to the old initial state
        for state in self.final_states:
            if state not in new_transitions:
                new_transitions[state] = dict()
            if '' not in new_transitions[state]:
                new_transitions[state][''] = set()
            new_transitions[state][''].add(self.initial_state)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=self.final_states | {new_initial_state}
        )

    def option(self):
        """
        Given an NFA which accepts the language L returns
        an NFA which accepts L repeated 0 or 1 times. (option - ?)
        Note: still you cannot pass empty string to the machine.
        """
        new_states = set(self.states)
        new_initial_state = NFA._add_new_state(new_states)

        # Transitions are the same with a few additions.
        new_transitions = copy.deepcopy(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {
            '': {self.initial_state}
        }

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=self.final_states | {new_initial_state}
        )

    def reverse(self):
        """
        Given an NFA which accepts the language L this function
        returns an NFA which accepts the reverse of L.
        """
        new_states = set(self.states)
        new_initial_state = NFA._add_new_state(new_states)

        # Transitions are the same except reversed
        new_transitions = {
            state: dict() for state in new_states
        }

        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                for state_b in states:
                    new_transitions[state_b].setdefault(symbol, set()).add(state_a)

        new_transitions[new_initial_state][''] = set()
        # And we additionally have epsilon transitions from
        # new initial state to each old final state.
        for state in self.final_states:
            new_transitions[new_initial_state][''].add(state)

        new_final_states = {self.initial_state}

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def show_diagram(self, path=None):
        """
            Creates the graph associated with this DFA
        """
        # Nodes are set of states

        graph = Dot(graph_type='digraph', rankdir='LR')
        nodes = {}
        for state in self.states:
            if state == self.initial_state:
                # color start state with green
                if state in self.final_states:
                    initial_state_node = Node(
                        state,
                        style='filled',
                        peripheries=2,
                        fillcolor='#66cc33')
                else:
                    initial_state_node = Node(
                        state, style='filled', fillcolor='#66cc33')
                nodes[state] = initial_state_node
                graph.add_node(initial_state_node)
            else:
                if state in self.final_states:
                    state_node = Node(state, peripheries=2)
                else:
                    state_node = Node(state)
                nodes[state] = state_node
                graph.add_node(state_node)
        # adding edges
        for from_state, lookup in self.transitions.items():
            for to_label, to_states in lookup.items():
                for to_state in to_states:
                    graph.add_edge(Edge(
                        nodes[from_state],
                        nodes[to_state],
                        label=to_label
                    ))
        if path:
            graph.write_png(path)
        return graph

    @staticmethod
    def _load_new_transition_dict(state_map_dict,
                                  old_transition_dict,
                                  new_transition_dict):
        """
        Load the new_transition_dict with the old transitions corresponding to
        the given state_map_dict.
        """

        for state_a, transitions in old_transition_dict.items():
            for symbol, states in transitions.items():
                new_transition_dict[state_map_dict[state_a]][symbol] = {
                    state_map_dict[state_b] for state_b in states
                }

    @staticmethod
    def _add_new_state(state_set, start=0):
        """Adds new state to the state set and returns it"""
        new_state = start
        while new_state in state_set:
            new_state += 1

        state_set.add(new_state)

        return new_state
