#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
from itertools import product
from collections import defaultdict, deque
from pydot import Dot, Edge, Node
from typing import Dict, Set, Generator, Deque, Iterable, Any, Optional, FrozenSet

import automata.fa.nfa as nfa
import automata.base.exceptions as exceptions
import automata.fa.fa as fa

DFAStateT = fa.FAStateT

GraphT = Dict[DFAStateT, Set[DFAStateT]]
DFAPathT = Dict[str, DFAStateT]
DFATransitionsT = Dict[DFAStateT, DFAPathT]

class DFA(fa.FA):
    """A deterministic finite automaton."""

    def __init__(self,
                 *,
                 states : Set[DFAStateT],
                 input_symbols : Set[str],
                 transitions : DFATransitionsT,
                 initial_state : DFAStateT,
                 final_states : Set[DFAStateT],
                 allow_partial : bool = False) -> None:
        """Initialize a complete DFA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.allow_partial = allow_partial
        self.validate()

    def __eq__(self, other : object) -> bool:
        """Return True if two DFAs are equivalent."""
        if isinstance(other, DFA):
            return self.symmetric_difference(other).isempty()
        return False

    def __le__(self, other : 'DFA') -> bool:
        """Return True if this DFA is a subset of (or equal to) another DFA."""
        if isinstance(other, DFA):
            return self.issubset(other)
        else:
            raise NotImplementedError

    def __ge__(self, other : 'DFA') -> bool:
        """Return True if this DFA is a superset of another DFA."""
        if isinstance(other, DFA):
            return self.issuperset(other)
        else:
            raise NotImplementedError

    def __lt__(self, other : 'DFA') -> bool:
        """Return True if this DFA is a strict subset of another DFA."""
        if isinstance(other, DFA):
            return self <= other and self != other
        else:
            raise NotImplementedError

    def __gt__(self, other : 'DFA') -> bool:
        """Return True if this DFA is a strict superset of another DFA."""
        if isinstance(other, DFA):
            return self >= other and self != other
        else:
            raise NotImplementedError

    def __sub__(self, other : 'DFA') -> 'DFA':
        """Return a DFA that is the difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.difference(other)
        else:
            raise NotImplementedError

    def __or__(self, other : 'DFA') -> 'DFA':
        """Return the union of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.union(other)
        else:
            raise NotImplementedError

    def __and__(self, other : 'DFA') -> 'DFA':
        """Return the intersection of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.intersection(other)
        else:
            raise NotImplementedError

    def __xor__(self, other : 'DFA') -> 'DFA':
        """Return the symmetric difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.symmetric_difference(other)
        else:
            raise NotImplementedError

    def __invert__(self) -> 'DFA':
        """Return the complement of this DFA and another DFA."""
        return self.complement()

    def _validate_transition_missing_symbols(self, start_state : DFAStateT, paths : DFAPathT) -> None:
        """Raise an error if the transition input_symbols are missing."""
        if self.allow_partial:
            return
        for input_symbol in self.input_symbols:
            if input_symbol not in paths:
                raise exceptions.MissingSymbolError(
                    'state {} is missing transitions for symbol {}'.format(
                        start_state, input_symbol))

    def _validate_transition_invalid_symbols(self, start_state : DFAStateT, paths : DFAPathT) -> None:
        """Raise an error if transition input symbols are invalid."""
        for input_symbol in paths.keys():
            if input_symbol not in self.input_symbols:
                raise exceptions.InvalidSymbolError(
                    'state {} has invalid transition symbol {}'.format(
                        start_state, input_symbol))

    def _validate_transition_start_states(self) -> None:
        """Raise an error if transition start states are missing."""
        for state in self.states:
            if state not in self.transitions:
                raise exceptions.MissingStateError(
                    'transition start state {} is missing'.format(
                        state))

    def _validate_transition_end_states(self, start_state : DFAStateT, paths : DFAPathT) -> None:
        """Raise an error if transition end states are invalid."""
        for end_state in paths.values():
            if end_state not in self.states:
                raise exceptions.InvalidStateError(
                    'end state {} for transition on {} is not valid'.format(
                        end_state, start_state))

    def _validate_transitions(self, start_state : DFAStateT, paths : DFAPathT) -> None:
        """Raise an error if transitions are missing or invalid."""
        self._validate_transition_missing_symbols(start_state, paths)
        self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_transition_end_states(start_state, paths)

    def validate(self) -> bool:
        """Return True if this DFA is internally consistent."""
        self._validate_transition_start_states()
        for start_state, paths in self.transitions.items():
            self._validate_transitions(start_state, paths)
        self._validate_initial_state()
        self._validate_final_states()
        return True

    def _get_next_current_state(self, current_state : DFAStateT, input_symbol : str) -> DFAStateT:
        """
        Follow the transition for the given input symbol on the current state.

        Raise an error if the transition does not exist.
        """
        if input_symbol in self.transitions[current_state]:
            return self.transitions[current_state][input_symbol]
        else:
            raise exceptions.RejectionException(
                '{} is not a valid input symbol'.format(input_symbol))

    def _check_for_input_rejection(self, current_state : DFAStateT) -> None:
        """Raise an error if the given config indicates rejected input."""
        if current_state not in self.final_states:
            raise exceptions.RejectionException(
                'the DFA stopped on a non-final state ({})'.format(
                    current_state))

    def read_input_stepwise(self, input_str : str) -> Generator[DFAStateT, None, None]:
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

    def minify(self, retain_names : bool = True) -> 'DFA':
        """
        Create a minimal DFA which accepts the same inputs as this DFA.

        First, non-reachable states are removed.
        Then, similiar states are merged using Hopcroft's Algorithm.
            retain_names: If True, merged states retain names.
                          If False, new states will be named 0, ..., n-1.
        """
        new_dfa = self.copy()
        new_dfa._remove_unreachable_states()
        new_dfa._merge_states(retain_names=retain_names)
        return new_dfa

    def _remove_unreachable_states(self) -> None:
        """Remove states which are not reachable from the initial state."""
        reachable_states = self._compute_reachable_states()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transitions[state]
            if state in self.final_states:
                self.final_states.remove(state)

    def _compute_reachable_states(self) -> Set[DFAStateT]:
        """Compute the states which are reachable from the initial state."""
        reachable_states = set()
        states_to_check : Deque[DFAStateT] = deque()
        states_to_check.append(self.initial_state)
        reachable_states.add(self.initial_state)
        while states_to_check:
            state = states_to_check.popleft()
            for symbol, dst_state in self.transitions[state].items():
                if dst_state not in reachable_states:
                    reachable_states.add(dst_state)
                    states_to_check.append(dst_state)
        return reachable_states

    def _merge_states(self, retain_names : bool = False) -> None:
        eq_classes_list = []
        if len(self.final_states) != 0:
            eq_classes_list.append(frozenset(self.final_states))
        if len(self.final_states) != len(self.states):
            eq_classes_list.append(
                frozenset(set(self.states).difference(self.final_states))
            )
        eq_classes = set(eq_classes_list)

        processing = set([frozenset(self.final_states)])

        while len(processing) > 0:
            active_state = processing.pop()
            for active_letter in self.input_symbols:
                states_that_move_into_active_state = frozenset(
                    state
                    for state in self.states
                    if self.transitions[state][active_letter] in active_state
                )

                copy_eq_classes = set(eq_classes)

                for checking_set in copy_eq_classes:
                    XintY = checking_set.intersection(
                        states_that_move_into_active_state
                    )
                    if len(XintY) == 0:
                        continue
                    XdiffY = checking_set.difference(
                        states_that_move_into_active_state
                    )
                    if len(XdiffY) == 0:
                        continue
                    eq_classes.remove(checking_set)
                    eq_classes.add(XintY)
                    eq_classes.add(XdiffY)
                    if checking_set in processing:
                        processing.remove(checking_set)
                        processing.add(XintY)
                        processing.add(XdiffY)
                    else:
                        if len(XintY) < len(XdiffY):
                            processing.add(XintY)
                        else:
                            processing.add(XdiffY)

        # now eq_classes are good to go, make them a list for ordering
        eq_classes_new = list(eq_classes)

        def rename(eq):
            return list(eq)[0] if len(eq) == 1 else DFA._stringify_states(eq)

        # need a backmap to prevent constant calls to index
        back_map = {}
        for i, eq in enumerate(eq_classes_new):
            name = rename(eq) if retain_names else str(i)
            for state in eq:
                back_map[state] = name

        new_input_symbols = self.input_symbols
        new_states = ({rename(eq) for eq in eq_classes_new} if retain_names
                      else set(str(i) for i in range(len(eq_classes_new))))
        new_initial_state = back_map[self.initial_state]
        new_final_states = set([back_map[acc] for acc in self.final_states])
        new_transitions : DFATransitionsT = {}
        for i, eq in enumerate(eq_classes_new):
            name = rename(eq) if retain_names else str(i)
            new_transitions[name] = {}
            for letter in self.input_symbols:
                new_transitions[name][letter] = back_map[
                    self.transitions[list(eq)[0]][letter]
                ]

        self.states = new_states
        self.input_symbols = new_input_symbols
        self.transitions = new_transitions
        self.initial_state = new_initial_state
        self.final_states = new_final_states

    def _cross_product(self, other : 'DFA') -> 'DFA':
        """
        Creates a new DFA which is the cross product of DFAs self and other
        with an empty set of final states.
        """
        assert self.input_symbols == other.input_symbols
        new_states = set(map(frozenset, product(self.states, other.states)))

        new_transitions : DFATransitionsT = dict()
        for state_a, transitions_a in self.transitions.items():
            for state_b, transitions_b in other.transitions.items():
                new_state = frozenset((state_a, state_b))
                new_transitions[new_state] = dict()
                for symbol in self.input_symbols:
                    new_transitions[new_state][symbol] = frozenset((
                        transitions_a[symbol], transitions_b[symbol]
                    ))

        new_initial_state = frozenset((self.initial_state, other.initial_state))

        return DFA(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=set()
        )

    def union(self, other : 'DFA', *, retain_names : bool = False, minify : bool = True) -> 'DFA':
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the union of L1 and L2.
        """
        new_dfa = self._cross_product(other)
        for state_a in self.states:
            for state_b in other.states:
                if (state_a in self.final_states or
                        state_b in other.final_states):
                    new_dfa.final_states.add(frozenset((state_a, state_b)))
        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def intersection(self, other : 'DFA', *, retain_names : bool = False, minify : bool = True) -> 'DFA':
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the intersection of L1 and L2.
        """
        new_dfa = self._cross_product(other)
        for state_a in self.final_states:
            for state_b in other.final_states:
                new_dfa.final_states.add(frozenset((state_a, state_b)))
        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def difference(self, other : 'DFA', *, retain_names : bool = False, minify : bool = True) -> 'DFA':
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the difference of L1 and L2.
        """
        new_dfa = self._cross_product(other)
        for state_a in self.final_states:
            for state_b in other.states:
                if state_b not in other.final_states:
                    new_dfa.final_states.add(frozenset((state_a, state_b)))
        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def symmetric_difference(self, other : 'DFA', *, retain_names : bool = False, minify : bool = True) -> 'DFA':
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the symmetric difference of L1 and L2.
        """
        new_dfa = self._cross_product(other)
        for state_a in self.states:
            for state_b in other.states:
                if ((state_a in self.final_states and
                        state_b not in other.final_states) or
                    (state_a not in self.final_states and
                        state_b in other.final_states)):
                    new_dfa.final_states.add(frozenset((state_a, state_b)))
        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def complement(self) -> 'DFA':
        """Return the complement of this DFA."""
        new_dfa = self.copy()
        new_dfa.final_states = frozenset(self.states - self.final_states)
        return new_dfa

    def issubset(self, other : 'DFA') -> bool:
        """Return True if this DFA is a subset of another DFA."""
        return self.intersection(other) == self

    def issuperset(self, other : 'DFA') -> bool:
        """Return True if this DFA is a superset of another DFA."""
        return other.issubset(self)

    def isdisjoint(self, other : 'DFA') -> bool:
        """Return True if this DFA has no common elements with another DFA."""
        return self.intersection(other).isempty()

    def isempty(self) -> bool:
        """Return True if this DFA is completely empty."""
        return len(self.minify().final_states) == 0

    def _make_graph(self) -> GraphT:
        """
        Returns a simple graph representation of the DFA.
        """
        G = defaultdict(set)
        for k, v in self.transitions.items():
            for c, u in v.items():
                G[k].add(u)
        return G

    def _reverse_graph(self, G : GraphT) -> GraphT:
        """
        Returns the graph G where all edges have been reversed.
        """
        rev_G = defaultdict(set)
        for k, v in G.items():
            for u in v:
                rev_G[u].add(k)
        return rev_G

    def _reachable_nodes(self, G : GraphT, v : DFAStateT, vis : Set[DFAStateT]) -> None:
        """
        Computes the set of reachable nodes
        in the graph G starting at vertex v.
        """
        if v not in vis:
            vis.add(v)
            for u in G[v]:
                self._reachable_nodes(G, u, vis)

    def _induced_subgraph(self, G : GraphT, S : Set[DFAStateT]) -> GraphT:
        """
        Computes the induced subgraph G[S].
        """
        return {k: {x for x in G[k] if x in S} for k in G if k in S}

    def _has_cycle(self, G : GraphT) -> bool:
        """
        Returns True if the graph G contains a cycle, False otherwise.
        """
        def dfs(G : GraphT, at : DFAStateT, vis : Set[DFAStateT], stack : Set[DFAStateT]) -> bool:
            """
            Helper function which accepts input parameters for
            the graph, current node, visited set and current stack
            """
            if at not in vis:
                vis.add(at)
                stack.add(at)
                for k in G[at]:
                    if k not in vis and dfs(G, k, vis, stack):
                        return True
                    elif k in stack:
                        # We have seen this vertex before in the path
                        return True
                stack.remove(at)
            return False
        vis : Set[DFAStateT] = set()
        stack : Set[DFAStateT] = set()
        return any(dfs(G, k, vis, stack) for k in G)

    def isfinite(self) -> bool:
        """
        Returns True if the DFA accepts a finite language, False otherwise.
        """
        G = self._make_graph()
        rev_G = self._reverse_graph(G)

        accessible_nodes : Set[DFAStateT] = set()
        self._reachable_nodes(G, self.initial_state, accessible_nodes)
        coaccessible_nodes : Set[DFAStateT] = set()
        for state in self.final_states:
            self._reachable_nodes(rev_G, state, coaccessible_nodes)

        important_nodes = accessible_nodes.intersection(coaccessible_nodes)

        constrained_G = self._induced_subgraph(G, important_nodes)

        contains_cycle = self._has_cycle(constrained_G)

        return not contains_cycle


    @staticmethod
    def _to_canonical_form(states : Iterable[DFAStateT]) -> FrozenSet[DFAStateT]:
        """Return a canonical (hashable) form of the given iterable of states."""
        return frozenset(states)

    @staticmethod
    def _stringify_states(states : Iterable[DFAStateT]) -> Any:
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(','.join(sorted(states))) #type: ignore

    @classmethod
    def _add_nfa_states_from_queue(cls,
                                   nfa : 'nfa.NFA',
                                   current_states : Set[DFAStateT],
                                   current_state_name : DFAStateT,
                                   dfa_states : Set[DFAStateT],
                                   dfa_transitions : DFATransitionsT,
                                   dfa_final_states : Set[DFAStateT]):
        """Add NFA states to DFA as it is constructed from NFA."""
        dfa_states.add(current_state_name)
        dfa_transitions[current_state_name] = {}
        if (current_states & nfa.final_states):
            dfa_final_states.add(current_state_name)

    @classmethod
    def _enqueue_next_nfa_current_states(cls,
                                         nfa : 'nfa.NFA',
                                         current_states : Set[DFAStateT],
                                         current_state_name : DFAStateT,
                                         state_queue : Deque[Set[DFAStateT]],
                                         dfa_transitions : DFATransitionsT):
        """Enqueue the next set of current states for the generated DFA."""
        for input_symbol in nfa.input_symbols:
            next_current_states = cls._to_canonical_form(
                nfa._get_next_current_states(current_states, input_symbol)
            )
            dfa_transitions[current_state_name][input_symbol] = \
                cls._to_canonical_form(next_current_states)
            state_queue.append(next_current_states)

    @classmethod
    def from_nfa(cls, nfa : 'nfa.NFA') -> 'DFA':
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states : Set[DFAStateT] = set()
        dfa_symbols = nfa.input_symbols
        dfa_transitions : DFATransitionsT = {}
        # equivalent DFA states states
        nfa_initial_states = cls._to_canonical_form(nfa._get_lambda_closure(nfa.initial_state))
        dfa_initial_state = nfa_initial_states
        dfa_final_states : Set[DFAStateT] = set()

        state_queue : Deque[FrozenSet[DFAStateT]] = deque()
        state_queue.append(nfa_initial_states)
        while state_queue:

            current_states = state_queue.popleft()
            current_state_name : DFAStateT = current_states
            if current_state_name in dfa_states:
                # We've been here before and nothing should have changed.
                continue

            cls._add_nfa_states_from_queue(nfa, current_states,
                                           current_state_name, dfa_states,
                                           dfa_transitions, dfa_final_states)
            cls._enqueue_next_nfa_current_states(
                nfa, current_states, current_state_name, state_queue,
                dfa_transitions)

        return cls(
            states=dfa_states, input_symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)

    def show_diagram(self, path : Optional[str] = None) -> Dot:
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
