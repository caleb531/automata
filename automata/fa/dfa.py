#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

from collections import deque
from enum import IntEnum
from itertools import chain, count, product

import networkx as nx

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.base.utils import PartitionRefinement
from frozendict import frozendict
from pydot import Dot, Edge, Node


class OriginEnum(IntEnum):
    SELF = 0
    OTHER = 1


class DFA(fa.FA):
    """A deterministic finite automaton."""

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_states, allow_partial=False):
        """Initialize a complete DFA."""
        super().__init__(
            states=frozenset(states),
            input_symbols=frozenset(input_symbols),
            transitions=frozendict({
                state: frozendict(paths)
                for state, paths in transitions.items()
            }),
            initial_state=initial_state,
            final_states=frozenset(final_states),
            allow_partial=allow_partial
        )

    def __eq__(self, other):
        """
        Return True if two DFAs are equivalent. Uses an optimized version of
        the Hopcroft-Karp algorithm. See https://arxiv.org/abs/0907.5058
        """

        origin_automata = {
            OriginEnum.SELF: self,
            OriginEnum.OTHER: other
        }

        # Must be another DFA and have equal alphabets
        if not isinstance(other, DFA) or self.input_symbols != other.input_symbols:
            return NotImplemented

        # Get new initial states
        initial_state_a = (self.initial_state, OriginEnum.SELF)
        initial_state_b = (other.initial_state, OriginEnum.OTHER)

        def is_final_state(state_pair):
            state, origin_enum = state_pair

            if origin_enum is OriginEnum.SELF:
                return state in self.final_states

            # origin_enum is OriginEnum.OTHER:
            return state in other.final_states

        def transition(state_pair, symbol):
            state, origin_enum = state_pair

            return (
                origin_automata[origin_enum]._get_next_current_state(
                    state, symbol),
                origin_enum
            )

        # Get data structures
        state_sets = nx.utils.union_find.UnionFind([initial_state_a, initial_state_b])
        pair_stack = deque()

        # Do union find
        state_sets.union(initial_state_a, initial_state_b)
        pair_stack.append((initial_state_a, initial_state_b))

        while pair_stack:
            q_a, q_b = pair_stack.pop()

            if is_final_state(q_a) ^ is_final_state(q_b):
                return False

            for symbol in self.input_symbols:

                r_1 = state_sets[transition(q_a, symbol)]
                r_2 = state_sets[transition(q_b, symbol)]

                if r_1 != r_2:
                    state_sets.union(r_1, r_2)
                    pair_stack.append((r_1, r_2))

        return True

    def __le__(self, other):
        """Return True if this DFA is a subset of (or equal to) another DFA."""
        if isinstance(other, DFA):
            return self.issubset(other)
        else:
            raise NotImplementedError

    def __ge__(self, other):
        """Return True if this DFA is a superset of another DFA."""
        if isinstance(other, DFA):
            return self.issuperset(other)
        else:
            raise NotImplementedError

    def __lt__(self, other):
        """Return True if this DFA is a strict subset of another DFA."""
        if isinstance(other, DFA):
            return self <= other and self != other
        else:
            raise NotImplementedError

    def __gt__(self, other):
        """Return True if this DFA is a strict superset of another DFA."""
        if isinstance(other, DFA):
            return self >= other and self != other
        else:
            raise NotImplementedError

    def __sub__(self, other):
        """Return a DFA that is the difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.difference(other)
        else:
            raise NotImplementedError

    def __or__(self, other):
        """Return the union of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.union(other)
        else:
            raise NotImplementedError

    def __and__(self, other):
        """Return the intersection of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.intersection(other)
        else:
            raise NotImplementedError

    def __xor__(self, other):
        """Return the symmetric difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.symmetric_difference(other)
        else:
            raise NotImplementedError

    def __invert__(self):
        """Return the complement of this DFA and another DFA."""
        return self.complement()

    def _validate_transition_missing_symbols(self, start_state, paths):
        """Raise an error if the transition input_symbols are missing."""
        if self.allow_partial:
            return
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
        if self.allow_partial:
            return
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

    def validate(self):
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
            raise exceptions.RejectionException(
                '{} is not a valid input symbol'.format(input_symbol))

    def _check_for_input_rejection(self, current_state):
        """Raise an error if the given config indicates rejected input."""
        if current_state not in self.final_states:
            raise exceptions.RejectionException(
                'the DFA stopped on a non-final state ({})'.format(
                    current_state))

    def read_input_stepwise(self, input_str):
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

    def _get_digraph(self):
        """Return a digraph corresponding to this DFA with transition symbols ignored"""
        return nx.DiGraph([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for end_state in transition.values()
        ])

    def _compute_reachable_states(self):
        """Compute the states which are reachable from the initial state."""
        visited_set = set()
        queue = deque()

        queue.append(self.initial_state)
        visited_set.add(self.initial_state)

        while queue:
            state = queue.popleft()

            for next_state in self.transitions[state].values():
                if next_state not in visited_set:
                    visited_set.add(next_state)
                    queue.append(next_state)

        return visited_set

    def minify(self, retain_names=False):
        """
        Create a minimal DFA which accepts the same inputs as this DFA.

        First, non-reachable states are removed.
        Then, similiar states are merged using Hopcroft's Algorithm.
            retain_names: If True, merged states retain names.
                          If False, new states will be named 0, ..., n-1.
        """

        # Compute reachable states and final states
        reachable_states = self._compute_reachable_states()
        reachable_final_states = self.final_states & reachable_states

        # First, assemble backmap and equivalence class data structure
        eq_classes = PartitionRefinement(reachable_states)
        refinement = eq_classes.refine(reachable_final_states)

        final_states_id = refinement[0][0] if refinement else eq_classes.get_set_ids()[0]

        transition_back_map = {
            symbol: {
                end_state: list()
                for end_state in reachable_states
            }
            for symbol in self.input_symbols
        }

        for start_state, path in self.transitions.items():
            if start_state in reachable_states:
                for symbol, end_state in path.items():
                    if end_state in reachable_states:
                        transition_back_map[symbol][end_state].append(start_state)

        origin_dicts = tuple(transition_back_map.values())
        processing = {final_states_id}

        while processing:
            # Save a copy of the set, since it could get modified while executing
            active_state = tuple(eq_classes.get_set_by_id(processing.pop()))
            for origin_dict in origin_dicts:
                states_that_move_into_active_state = chain.from_iterable(
                    origin_dict[end_state] for end_state in active_state
                )

                # Refine set partition by states moving into current active one
                new_eq_class_pairs = eq_classes.refine(states_that_move_into_active_state)

                for (YintX_id, YdiffX_id) in new_eq_class_pairs:
                    # Only adding one id to processing, since the other is already there
                    if YdiffX_id in processing:
                        processing.add(YintX_id)
                    else:
                        if len(eq_classes.get_set_by_id(YintX_id)) <= len(eq_classes.get_set_by_id(YdiffX_id)):
                            processing.add(YintX_id)
                        else:
                            processing.add(YdiffX_id)

        # now eq_classes are good to go, make them a list for ordering
        eq_class_name_pairs = (
            [(frozenset(eq), eq) for eq in eq_classes.get_sets()] if retain_names else
            list(enumerate(eq_classes.get_sets()))
        )

        # need a backmap to prevent constant calls to index
        back_map = {
            state: name
            for name, eq in eq_class_name_pairs
            for state in eq
        }

        new_input_symbols = self.input_symbols
        new_states = set(back_map.values())
        new_initial_state = back_map[self.initial_state]
        new_final_states = {back_map[acc] for acc in reachable_final_states}
        new_transitions = {
            name: {
                letter: back_map[self.transitions[next(iter(eq))][letter]]
                for letter in self.input_symbols
            }
            for name, eq in eq_class_name_pairs
        }

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
        )

    def _cross_product(self, other, final_states):
        """
        Creates a new DFA which is the cross product of DFAs self and other
        with an empty set of final states.
        """
        if self.input_symbols != other.input_symbols:
            raise exceptions.SymbolMismatchError('The input symbols between the two given DFAs do not match')

        new_states = set(product(self.states, other.states))

        new_transitions = {
            (state_a, state_b): {
                symbol: (transitions_a[symbol], transitions_b[symbol])
                for symbol in self.input_symbols
            }
            for (state_a, transitions_a), (state_b, transitions_b) in
            product(self.transitions.items(), other.transitions.items())
        }

        new_initial_state = (self.initial_state, other.initial_state)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=final_states
        )

    def union(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the union of L1 and L2.
        """

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in product(self.states, other.states)
            if (state_a in self.final_states or state_b in other.final_states)
        }

        new_dfa = self._cross_product(other, new_final_states)

        if minify:
            return new_dfa.minify(retain_names=retain_names)

        return new_dfa

    def intersection(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the intersection of L1 and L2.
        """

        new_final_states = set(product(self.final_states, other.final_states))
        new_dfa = self._cross_product(other, new_final_states)

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def difference(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the difference of L1 and L2.
        """

        new_final_states = set(product(self.final_states, other.states - other.final_states))
        new_dfa = self._cross_product(other, new_final_states)

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def symmetric_difference(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the symmetric difference of L1 and L2.
        """

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in product(self.states, other.states)
            if (state_a in self.final_states) ^ (state_b in other.final_states)
        }

        new_dfa = self._cross_product(other, new_final_states)

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def complement(self):
        """Return the complement of this DFA."""

        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.states - self.final_states,
            allow_partial=self.allow_partial
        )

    def _get_reachable_states_product_graph(self, other):
        """Get reachable states corresponding to product graph between self and other"""
        if self.input_symbols != other.input_symbols:
            raise exceptions.SymbolMismatchError('The input symbols between the two given DFAs do not match')

        visited_set = set()
        queue = deque()

        product_initial_state = (self.initial_state, other.initial_state)
        queue.append(product_initial_state)
        visited_set.add(product_initial_state)

        while queue:
            q_a, q_b = queue.popleft()

            for chr in self.input_symbols:
                product_state = (self.transitions[q_a][chr], other.transitions[q_b][chr])

                if product_state not in visited_set:
                    visited_set.add(product_state)
                    queue.append(product_state)

        return visited_set

    def issubset(self, other):
        """Return True if this DFA is a subset of another DFA."""
        for (state_a, state_b) in self._get_reachable_states_product_graph(other):
            # Check for reachable state that is counterexample to subset
            if state_a in self.final_states and state_b not in other.final_states:
                return False

        return True

    def issuperset(self, other):
        """Return True if this DFA is a superset of another DFA."""
        return other.issubset(self)

    def isdisjoint(self, other):
        """Return True if this DFA has no common elements with another DFA."""
        for (state_a, state_b) in self._get_reachable_states_product_graph(other):
            # Check for reachable state that is counterexample to disjointness
            if state_a in self.final_states and state_b in other.final_states:
                return False

        return True

    def isempty(self):
        """Return True if this DFA is completely empty."""
        return len(self._compute_reachable_states() & self.final_states) == 0

    def isfinite(self):
        """
        Returns True if the DFA accepts a finite language, False otherwise.
        """
        G = self._get_digraph()

        accessible_nodes = nx.descendants(G, self.initial_state) | {self.initial_state}

        coaccessible_nodes = self.final_states.union(*(
            nx.ancestors(G, state)
            for state in self.final_states
        ))

        important_nodes = accessible_nodes.intersection(coaccessible_nodes)

        try:
            nx.find_cycle(G.subgraph(important_nodes))
            return False
        except nx.exception.NetworkXNoCycle:
            return True

    @classmethod
    def from_nfa(cls, target_nfa, retain_names=False):
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states = set()
        dfa_symbols = target_nfa.input_symbols
        dfa_transitions = {}

        # Data structures for state renaming
        new_state_name_dict = dict()
        state_name_counter = count(0)

        def get_name_renamed(states):
            nonlocal state_name_counter, new_state_name_dict
            return new_state_name_dict.setdefault(states, next(state_name_counter))

        def get_name_original(states):
            return states

        get_name = get_name_original if retain_names else get_name_renamed

        # equivalent DFA states states
        nfa_initial_states = frozenset(target_nfa.lambda_closures[target_nfa.initial_state])
        dfa_initial_state = get_name(nfa_initial_states)
        dfa_final_states = set()

        state_queue = deque()
        state_queue.append(nfa_initial_states)
        while state_queue:
            current_states = state_queue.popleft()
            current_state_name = get_name(current_states)
            if current_state_name in dfa_states:
                # We've been here before and nothing should have changed.
                continue

            # Add NFA states to DFA as it is constructed from NFA.
            dfa_states.add(current_state_name)
            dfa_transitions[current_state_name] = {}
            if (current_states & target_nfa.final_states):
                dfa_final_states.add(current_state_name)

            # Enqueue the next set of current states for the generated DFA.
            for input_symbol in target_nfa.input_symbols:
                next_current_states = frozenset(target_nfa._get_next_current_states(
                    current_states, input_symbol))
                dfa_transitions[current_state_name][input_symbol] = get_name(next_current_states)
                state_queue.append(next_current_states)

        return cls(
            states=dfa_states, input_symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)

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
            for to_label, to_state in lookup.items():
                graph.add_edge(Edge(
                    nodes[from_state],
                    nodes[to_state],
                    label=to_label
                ))
        if path:
            graph.write_png(path)
        return graph
