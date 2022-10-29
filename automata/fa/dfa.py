#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

from collections import defaultdict, deque
from itertools import chain, count

import networkx as nx
from pydot import Dot, Edge, Node

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.base.utils import PartitionRefinement


class DFA(fa.FA):
    """A deterministic finite automaton."""

    __slots__ = ('states', 'input_symbols', 'transitions',
                 'initial_state', 'final_states', 'allow_partial')

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_states, allow_partial=False):
        """Initialize a complete DFA."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
            allow_partial=allow_partial
        )
        object.__setattr__(self, '_word_cache', [])
        object.__setattr__(self, '_count_cache', [])

    def __eq__(self, other):
        """
        Return True if two DFAs are equivalent. Uses an optimized version of
        the Hopcroft-Karp algorithm. See https://arxiv.org/abs/0907.5058
        """

        # Must be another DFA and have equal alphabets
        if not isinstance(other, DFA) or self.input_symbols != other.input_symbols:
            return NotImplemented

        operand_dfas = (self, other)
        initial_state_a = (self.initial_state, 0)
        initial_state_b = (other.initial_state, 1)

        def is_final_state(state_pair):
            state, operand_index = state_pair
            return state in operand_dfas[operand_index].final_states

        def transition(state_pair, symbol):
            state, operand_index = state_pair
            return (
                operand_dfas[operand_index]._get_next_current_state(
                    state, symbol),
                operand_index
            )

        # Get data structures
        state_sets = nx.utils.union_find.UnionFind((initial_state_a, initial_state_b))
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
            return NotImplemented

    def __ge__(self, other):
        """Return True if this DFA is a superset of another DFA."""
        if isinstance(other, DFA):
            return self.issuperset(other)
        else:
            return NotImplemented

    def __lt__(self, other):
        """Return True if this DFA is a strict subset of another DFA."""
        if isinstance(other, DFA):
            return self <= other and self != other
        else:
            return NotImplemented

    def __gt__(self, other):
        """Return True if this DFA is a strict superset of another DFA."""
        if isinstance(other, DFA):
            return self >= other and self != other
        else:
            return NotImplemented

    def __sub__(self, other):
        """Return a DFA that is the difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.difference(other)
        else:
            return NotImplemented

    def __or__(self, other):
        """Return the union of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.union(other)
        else:
            return NotImplemented

    def __and__(self, other):
        """Return the intersection of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.intersection(other)
        else:
            return NotImplemented

    def __xor__(self, other):
        """Return the symmetric difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.symmetric_difference(other)
        else:
            return NotImplemented

    def __invert__(self):
        """Return the complement of this DFA and another DFA."""
        return self.complement()

    def __iter__(self):
        """
        Iterates through all words in the language represented by the DFA.
        The words are ordered first by length and then by the order of the input symbol set.
        """
        i = self.minimum_word_length()
        limit = self.maximum_word_length()
        while limit is None or i <= limit:
            yield from self.words_of_length(i)
            i += 1

    def __len__(self):
        """Returns the cardinality of the language represented by the DFA."""
        return self.cardinality()

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

        return self._minify(
            reachable_states=reachable_states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            reachable_final_states=reachable_final_states,
            retain_names=retain_names)

    @classmethod
    def _minify(cls, *, reachable_states, input_symbols, transitions, initial_state,
                reachable_final_states, retain_names):
        """Minify helper function. DFA data passed in must have no unreachable states."""

        # First, assemble backmap and equivalence class data structure
        eq_classes = PartitionRefinement(reachable_states)
        refinement = eq_classes.refine(reachable_final_states)

        final_states_id = refinement[0][0] if refinement else next(iter(eq_classes.get_set_ids()))

        transition_back_map = {
            symbol: {
                end_state: list()
                for end_state in reachable_states
            }
            for symbol in input_symbols
        }

        for start_state, path in transitions.items():
            if start_state in reachable_states:
                for symbol, end_state in path.items():
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

        new_input_symbols = input_symbols
        new_states = set(back_map.values())
        new_initial_state = back_map[initial_state]
        new_final_states = {back_map[acc] for acc in reachable_final_states}
        new_transitions = {
            name: {
                letter: back_map[transitions[next(iter(eq))][letter]]
                for letter in input_symbols
            }
            for name, eq in eq_class_name_pairs
        }

        return cls(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
        )

    def _cross_product(self, other):
        """
        Creates a new DFA which is the cross product of DFAs self and other
        with an empty set of final states.
        """
        if self.input_symbols != other.input_symbols:
            raise exceptions.SymbolMismatchError('The input symbols between the two given DFAs do not match')

        new_states = self._get_reachable_states_product_graph(other)

        new_transitions = {
            (state_a, state_b): {
                symbol: (self.transitions[state_a][symbol], other.transitions[state_b][symbol])
                for symbol in self.input_symbols
            }
            for (state_a, state_b) in new_states
        }

        new_initial_state = (self.initial_state, other.initial_state)

        return new_states, new_transitions, new_initial_state

    def union(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the union of L1 and L2.
        """

        new_states, new_transitions, new_initial_state = self._cross_product(other)

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in new_states
            if state_a in self.final_states or state_b in other.final_states
        }

        if minify:
            return self._minify(
                reachable_states=new_states,
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=new_initial_state,
                reachable_final_states=new_final_states,
                retain_names=retain_names)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def intersection(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the intersection of L1 and L2.
        """

        new_states, new_transitions, new_initial_state = self._cross_product(other)

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in new_states
            if state_a in self.final_states and state_b in other.final_states
        }

        if minify:
            return self._minify(
                reachable_states=new_states,
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=new_initial_state,
                reachable_final_states=new_final_states,
                retain_names=retain_names)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def difference(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the difference of L1 and L2.
        """
        new_states, new_transitions, new_initial_state = self._cross_product(other)

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in new_states
            if state_a in self.final_states and state_b not in other.final_states
        }

        if minify:
            return self._minify(
                reachable_states=new_states,
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=new_initial_state,
                reachable_final_states=new_final_states,
                retain_names=retain_names)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def symmetric_difference(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the symmetric difference of L1 and L2.
        """

        new_states, new_transitions, new_initial_state = self._cross_product(other)

        new_final_states = {
            (state_a, state_b)
            for state_a, state_b in new_states
            if (state_a in self.final_states) ^ (state_b in other.final_states)
        }

        if minify:
            return self._minify(
                reachable_states=new_states,
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=new_initial_state,
                reachable_final_states=new_final_states,
                retain_names=retain_names)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def complement(self, *, retain_names=False, minify=True):
        """Return the complement of this DFA."""

        if minify:
            reachable_states = self._compute_reachable_states()
            reachable_final_states = self.final_states & reachable_states

            return self._minify(
                reachable_states=reachable_states,
                input_symbols=self.input_symbols,
                transitions=self.transitions,
                initial_state=self.initial_state,
                reachable_final_states=reachable_states - reachable_final_states,
                retain_names=retain_names)

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
        try:
            return self.maximum_word_length() is not None
        except ValueError:
            return True

    def count_words_of_length(self, k):
        """
        Counts words of length `k` accepted by the DFA
        """
        self._ensure_count_for_length(k)
        return self._count_cache[k][self.initial_state]

    def _ensure_count_for_length(self, k):
        """
        Populate count cache up to length k
        """
        while len(self._count_cache) <= k:
            i = len(self._count_cache)
            self._count_cache.append(defaultdict(int))
            level = self._count_cache[i]
            if i == 0:
                level.update({state: 1 for state in self.final_states})
            else:
                prev_level = self._count_cache[i-1]
                level.update({
                    state: sum(prev_level[suffix_state] for suffix_state in self.transitions[state].values())
                    for state in self.states
                })

    def words_of_length(self, k):
        """
        Generates all words of size k in the language represented by the DFA
        """
        self._ensure_words_of_length(k)
        for word in self._word_cache[k][self.initial_state]:
            yield word

    def _ensure_words_of_length(self, k):
        """
        Populate word cache up to length k
        """
        sorted_symbols = sorted(self.input_symbols)
        while len(self._word_cache) <= k:
            i = len(self._word_cache)
            self._word_cache.append(defaultdict(list))
            level = self._word_cache[i]
            if i == 0:
                level.update({state: [''] for state in self.final_states})
            else:
                prev_level = self._word_cache[i-1]
                level.update({
                    state: [symbol+word
                            for symbol in sorted_symbols
                            for word in prev_level[self.transitions[state][symbol]]]
                    for state in self.states
                })

    def cardinality(self):
        """Returns the cardinality of the language represented by the DFA."""
        try:
            i = self.minimum_word_length()
        except ValueError:
            return 0
        limit = self.maximum_word_length()
        if limit is None:
            raise ValueError("The language represented by the DFA is infinite.")
        return sum(self.count_words_of_length(j) for j in range(i, limit+1))

    def minimum_word_length(self):
        """
        Returns the length of the shortest word in the language represented by the DFA
        """
        queue = deque()
        distances = defaultdict(lambda: None)
        distances[self.initial_state] = 0
        queue.append(self.initial_state)
        while queue:
            state = queue.popleft()
            if state in self.final_states:
                return distances[state]
            for next_state in self.transitions[state].values():
                if distances[next_state] is None:
                    distances[next_state] = distances[state] + 1
                    queue.append(next_state)
        raise ValueError('The language represented by the DFA is empty')

    def maximum_word_length(self):
        """
        Returns the length of the longest word in the language represented by the DFA
        In the case of infinite languages, `None` is returned
        """
        if self.isempty():
            raise ValueError('The language represented by the DFA is empty')
        G = self._get_digraph()

        accessible_nodes = nx.descendants(G, self.initial_state) | {self.initial_state}

        coaccessible_nodes = self.final_states.union(*(
            nx.ancestors(G, state)
            for state in self.final_states
        ))

        important_nodes = accessible_nodes.intersection(coaccessible_nodes)
        subgraph = G.subgraph(important_nodes)
        try:
            return nx.dag_longest_path_length(subgraph)
        except nx.exception.NetworkXUnfeasible:
            return None

    @classmethod
    def from_prefix(cls, input_symbols, prefix, *, contains=True):
        """
        Directly computes the minimal DFA recognizing strings with the
        given prefix.
        If contains is set to False then the complement is constructed instead.
        """
        err_state = -1
        last_state = len(prefix)
        transitions = {i: {symbol: i+1 if symbol == char else err_state
                           for symbol in input_symbols}
                       for i, char in enumerate(prefix)}
        transitions[last_state] = {symbol: last_state for symbol in input_symbols}
        transitions[err_state] = {symbol: err_state for symbol in input_symbols}
        states = set(transitions.keys())
        final_states = {last_state}
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states
        )

    @classmethod
    def from_suffix(cls, input_symbols, suffix, *, contains=True):
        """
        Directly computes the minimal DFA recognizing strings with the
        given prefix.
        If contains is set to False then the complement is constructed instead.
        """
        return cls.from_substring(input_symbols, suffix, contains=contains, must_be_suffix=True)

    @classmethod
    def from_substring(cls, input_symbols, substring, *, contains=True, must_be_suffix=False):
        """
        Directly computes the minimal DFA recognizing strings containing the
        given substring.
        If contains is set to False then the complement is constructed instead.
        If must_be_suffix is set to True, then the substring must be a suffix instead.
        """
        transitions = {i: dict() for i in range(len(substring))}
        transitions[len(substring)] = {
            symbol: len(substring) for symbol in input_symbols
        }

        # Computing failure function for partial matches as is done in the
        # Knuth-Morris-Pratt string algorithm so we can quickly compute the
        # next state from another state
        kmp_table = [-1 for _ in substring]
        candidate = 0
        for i, char in enumerate(substring):
            if i == 0:
                continue
            elif char == substring[candidate]:
                kmp_table[i] = kmp_table[candidate]
            else:
                kmp_table[i] = candidate
                while candidate >= 0 and char != substring[candidate]:
                    candidate = kmp_table[candidate]
            candidate += 1
        kmp_table.append(candidate)

        limit = len(substring)+1 if must_be_suffix else len(substring)
        for i in range(limit):
            prefix_dict = transitions.setdefault(i, dict())
            for symbol in input_symbols:
                # Look for next state after reading in the given input symbol
                candidate = i if i < len(substring) else kmp_table[i]
                while candidate != -1 and substring[candidate] != symbol:
                    candidate = kmp_table[candidate]
                candidate += 1
                prefix_dict[symbol] = candidate

        states = set(transitions.keys())
        final_states = {len(substring)}
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
        )

    @classmethod
    def from_subsequence(cls, input_symbols, subsequence, *, contains=True):
        """
        Directly computes the minimal DFA recognizing strings containing the
        given subsequence.
        If contains is set to False then the complement is constructed instead.
        """
        transitions = {0: {symbol: 0 for symbol in input_symbols}}

        for prev_state, char in enumerate(subsequence):
            next_state = prev_state + 1
            transitions[next_state] = {symbol: next_state for symbol in input_symbols}
            transitions[prev_state][char] = next_state

        states = set(transitions.keys())
        final_states = {len(subsequence)}
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
        )

    @classmethod
    def of_length(cls, input_symbols, *, min_length=0, max_length=None):
        """
        Directly computes the minimal DFA recognizing strings whose length
        is between `min_length` and `max_length`, inclusive.
        To allow infinitely long words the value `None` can be passed in for `max_length`.
        """
        transitions = {}
        length_range = range(min_length) if max_length is None else range(max_length+1)
        for prev_state in length_range:
            next_state = prev_state + 1
            transitions[prev_state] = {symbol: next_state for symbol in input_symbols}
        last_state = len(transitions)
        transitions[last_state] = {symbol: last_state for symbol in input_symbols}
        final_states = {last_state} if max_length is None else set(range(min_length, max_length+1))
        return cls(
            states=set(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states,
        )

    @classmethod
    def count_mod(cls, input_symbols, k, *, remainders=None, symbols_to_count=None):
        """
        Directly computes a DFA that counts given symbols and accepts all strings where
        the remainder of division by k is in the set of remainders given.
        The default value of remainders is {0} and all symbols are counted by default.
        """
        if k <= 0:
            raise ValueError("Integer must be positive")
        if symbols_to_count is None:
            symbols_to_count = input_symbols
        if remainders is None:
            remainders = {0}
        transitions = {i: {symbol: (i + 1) % k if symbol in symbols_to_count else i
                           for symbol in input_symbols}
                       for i in range(k)}
        return cls(
            states=set(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=remainders
        )

    @classmethod
    def universal_language(cls, input_symbols):
        """
        Directly computes the minimal DFA accepting all strings.
        """
        return cls(
            states={0},
            input_symbols=input_symbols,
            transitions={0: {symbol: 0 for symbol in input_symbols}},
            initial_state=0,
            final_states={0}
        )

    @classmethod
    def empty_language(cls, input_symbols):
        """
        Directly computes the minimal DFA rejecting all strings.
        """
        return cls(
            states={0},
            input_symbols=input_symbols,
            transitions={0: {symbol: 0 for symbol in input_symbols}},
            initial_state=0,
            final_states=set()
        )

    @classmethod
    def nth_from_start(cls, input_symbols, symbol, n):
        """
        Directly computes the minimal DFA which accepts all words whose `n`-th
        character from the start is `symbol`, where `n` is a positive integer.
        """
        if n < 1:
            raise ValueError("Integer must be positive")
        if symbol not in input_symbols:
            raise exceptions.InvalidSymbolError("Desired symbol is not in the set of input symbols")
        if len(input_symbols) == 1:
            return cls.of_length(input_symbols, min_length=n)
        transitions = {i: {symbol: i+1 for symbol in input_symbols} for i in range(n)}
        transitions[n-1][symbol] = n+1
        transitions[n] = {symbol: n for symbol in input_symbols}
        transitions[n+1] = {symbol: n+1 for symbol in input_symbols}
        return cls(
            states=set(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states={n+1}
        )

    @classmethod
    def nth_from_end(cls, input_symbols, symbol, n):
        """
        Directly computes the minimal DFA which accepts all words whose `n`-th
        character from the end is `symbol`, where `n` is a positive integer.
        """
        if n < 1:
            raise ValueError("Integer must be positive")
        if symbol not in input_symbols:
            raise exceptions.InvalidSymbolError("Desired symbol is not in the set of input symbols")
        if len(input_symbols) == 1:
            return cls.of_length(input_symbols, min_length=n)
        # Consider the states to be labelled with bitstrings of size n
        # The bitstring represents how the current suffix in this state matches our desired symbol
        # A 1 means the character at this position is the desired symbol and a 0 means it is not
        # For transitions this is effectively doubling the label value and then adding 1 if the desired symbol is read
        # Finally we trim the label to n bits with a modulo operation.
        state_count = 2**n
        return cls(
            states=set(range(state_count)),
            input_symbols=input_symbols,
            transitions={state: {sym: (2 * state + 1) % state_count
                                 if symbol == sym else (2 * state) % state_count
                                 for sym in input_symbols}
                         for state in range(state_count)},
            initial_state=0,
            final_states=set(range(state_count//2, state_count)),
        )

    @classmethod
    def from_finite_language(cls, input_symbols, language):
        """
        Directly computes the minimal DFA corresponding to a finite language.
        Uses the algorithm described in Finite-State Techniques by Mihov and Schulz,
        Chapter 10
        """

        if not language:
            return DFA.empty_language(input_symbols)

        transitions = dict()
        back_map = {'': set()}
        final_states = set()
        signatures_dict = dict()

        def compute_signature(state):
            """Computes signature for input state"""
            state_transition = transitions[state]
            return (state in final_states, frozenset(
                (chr, state_transition[chr]) for chr in state_transition
            ))

        def longest_common_prefix_length(string_1, string_2):
            """Returns length of longest common prefix."""
            for i, (chr_1, chr_2) in enumerate(zip(string_1, string_2)):
                if chr_1 != chr_2:
                    return i

            return min(len(string_1), len(string_2))

        def add_to_trie(word):
            """Add word to the trie represented by transitions"""
            prefix = ''
            for chr in word:
                next_prefix = prefix + chr

                # Extend the trie only if necessary
                prefix_dict = transitions.setdefault(prefix, dict())
                prefix_dict.setdefault(chr, next_prefix)
                back_map.setdefault(next_prefix, set()).add(prefix)

                prefix = next_prefix

            # Mark the finished prefix as a final state
            transitions[prefix] = dict()
            final_states.add(prefix)

        def compress(word, next_word):
            """Compress prefixes of word, newly added to the DFA"""

            # Compress along all prefixes that are _not_ prefixes of the next word
            lcp_len = longest_common_prefix_length(word, next_word)

            # Compression in order of reverse length
            for i in range(len(word), lcp_len, -1):
                prefix = word[:i]

                # Compute signature for comparison
                prefix_signature = compute_signature(prefix)
                identical_state = signatures_dict.get(prefix_signature)

                if identical_state is not None:
                    # If identical state exists, remove prefix since it's redundant
                    final_states.discard(prefix)
                    transitions.pop(prefix)

                    # Change transition for prefix
                    for parent_state in back_map[prefix]:
                        path = transitions[parent_state]
                        for chr in path:
                            if path[chr] == prefix:
                                path[chr] = identical_state
                        back_map[identical_state].add(parent_state)

                        # No need to recompute signatures here, since we will
                        # recompute when handling parents in later iterations
                else:
                    signatures_dict[prefix_signature] = prefix

        # Construct initial trie
        prev_word, *rest_words = sorted(language)
        add_to_trie(prev_word)

        for curr_word in rest_words:
            # For each word, compress from the previous iteration and continue
            compress(prev_word, curr_word)
            add_to_trie(curr_word)
            prev_word = curr_word

        compress(prev_word, '')

        # Add dump state. Always needed since dict is finite
        dump_state = 0
        transitions[dump_state] = {chr: dump_state for chr in input_symbols}

        for path in transitions.values():
            for chr in input_symbols:
                path.setdefault(chr, dump_state)

        return cls(
            states=set(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state='',
            final_states=final_states,
        )

    @classmethod
    def from_nfa(cls, target_nfa, *, retain_names=False, minify=True):
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
        nfa_initial_states = frozenset(target_nfa._lambda_closures[target_nfa.initial_state])
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
                next_current_states = target_nfa._get_next_current_states(
                    current_states, input_symbol)
                dfa_transitions[current_state_name][input_symbol] = get_name(next_current_states)
                state_queue.append(next_current_states)

        if minify:
            return cls._minify(
                reachable_states=dfa_states,
                input_symbols=dfa_symbols,
                transitions=dfa_transitions,
                initial_state=dfa_initial_state,
                reachable_final_states=dfa_final_states,
                retain_names=retain_names)

        return cls(
            states=dfa_states,
            input_symbols=dfa_symbols,
            transitions=dfa_transitions,
            initial_state=dfa_initial_state,
            final_states=dfa_final_states)

    @classmethod
    def levenshtein(cls, input_symbols, query, D):
        """Code adapted from https://fulmicoton.com/posts/levenshtein/"""
        def transitions(state, chi):
            (offset, D) = state
            if D > 0:
                yield (offset, D - 1)
                yield (offset + 1, D - 1)
            for (d, val) in enumerate(chi[offset:]):
                if val:
                    yield offset + d + 1, D - d


        def simplify(states):
            def implies(state1, state2):
                """
                Returns true, if state1 implies state2
                """
                (offset, D) = state1
                (offset2, D2) = state2
                if D2 < 0:
                    return True
                return D - D2 >= abs(offset2 - offset)

            def is_useful(s):
                for s2 in states:
                    if s != s2 and implies(s2, s):
                        return False
                return True

            return filter(is_useful, states)

        def characteristic(c):
            return tuple(
                v == c
                for (offset, v) in enumerate(query)
            )

        def step(c, states):
            next_states = set()
            for state in states:
                next_states |= set(transitions(state, c))
            states = simplify(next_states)
            return states


        accepting_states = set()
        transitions_dict = dict()
        start_state = frozenset({(0, D)})
        states = {start_state}

        state_queue = deque()
        state_queue.append(start_state)

        while state_queue:
            state_set = state_queue.popleft()
            state_transition_dict = transitions_dict.setdefault(state_set, dict())

            for c in input_symbols:
                chi = characteristic(c)
                next_states = frozenset(step(chi, state_set))
                state_transition_dict[c] = next_states

                if next_states not in states:
                    states.add(next_states)
                    state_queue.append(next_states)

                    for state in next_states:
                        (offset, c) = state
                        if len(query) - offset <= D:
                            accepting_states.add(next_states)
                            break

        #print(transitions_dict)
        #print(states)
        return DFA(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions_dict,
            initial_state=start_state,
            final_states=accepting_states,
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
            for to_label, to_state in lookup.items():
                graph.add_edge(Edge(
                    nodes[from_state],
                    nodes[to_state],
                    label=to_label
                ))
        if path:
            graph.write_png(path)
        return graph
