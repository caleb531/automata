#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""
from collections import deque
from itertools import chain, count, product

import networkx as nx
from frozendict import frozendict
from pydot import Dot, Edge, Node

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.regex.parser import RESERVED_CHARACTERS, parse_regex


class NFA(fa.FA):
    """A nondeterministic finite automaton."""

    __slots__ = ('states', 'input_symbols', 'transitions',
                 'initial_state', 'final_states')

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_states):
        """Initialize a complete NFA."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
            _lambda_closures=self._compute_lambda_closures(states, transitions)
        )

    def _compute_lambda_closures(self, states, transitions):
        """
        Computes a dictionary of the lambda closures for this NFA, where each
        key is the state name and the value is the lambda closure for that
        corresponding state. This dictionary is cached for the lifetime of the
        instance, and is available via the 'lambda_closures' attribute.

        The lambda closure of a state q is the set containing q, along with
        every state that can be reached from q by following only lambda
        transitions.
        """
        lambda_graph = nx.DiGraph()
        lambda_graph.add_nodes_from(states)
        lambda_graph.add_edges_from([
            (start_state, end_state)
            for start_state, transition in transitions.items()
            for char, end_states in transition.items()
            if char == ''
            for end_state in end_states
        ])

        return frozendict({
            state: frozenset(nx.descendants(lambda_graph, state) | {state})
            for state in states
        })

    def __add__(self, other):
        """Return the concatenation of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.concatenate(other)
        else:
            return NotImplemented

    def __or__(self, other):
        """Return the union of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.union(other)
        else:
            return NotImplemented

    def __and__(self, other):
        """Return the union of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.intersection(other)
        else:
            return NotImplemented

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
    def from_regex(cls, regex, *, input_symbols=None):
        """Initialize this NFA as one equivalent to the given regular expression"""

        if input_symbols is None:
            input_symbols = set(regex) - RESERVED_CHARACTERS
        else:
            conflicting_symbols = RESERVED_CHARACTERS & input_symbols
            if conflicting_symbols:
                raise exceptions.InvalidSymbolError(f'Invalid input symbols: {conflicting_symbols}')

        nfa_builder = parse_regex(regex, input_symbols)

        return cls(
            states=frozenset(nfa_builder._transitions.keys()),
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
                    self._lambda_closures[end_state])

        return frozenset(next_current_states)

    @staticmethod
    def _compute_reachable_states(initial_state, input_symbols, transitions):
        """Compute the states which are reachable from the initial state."""

        visited_set = set()
        queue = deque()

        queue.append(initial_state)
        visited_set.add(initial_state)

        while queue:
            state = queue.popleft()
            state_dict = transitions.get(state)

            if state_dict:
                for next_state in chain.from_iterable(dest for dest in state_dict.values()):
                    if next_state not in visited_set:
                        visited_set.add(next_state)
                        queue.append(next_state)

        return visited_set

    def _eliminate_lambda(self):
        """Internal helper function for eliminate lambda. Doesn't create final NFA."""

        # Create new transitions and final states for running this algorithm
        new_transitions = {
            state: {
                symbol: set(dest)
                for symbol, dest in paths.items()
            }
            for state, paths in self.transitions.items()
        }
        new_final_states = set(self.final_states)

        for state in self.states:
            lambda_enclosure = self._lambda_closures[state] - {state}
            for input_symbol in self.input_symbols:
                next_current_states = self._get_next_current_states(lambda_enclosure, input_symbol)

                # Don't do anything if no new current states
                if next_current_states:
                    state_transition_dict = new_transitions.setdefault(state, {})

                    if input_symbol in state_transition_dict:
                        state_transition_dict[input_symbol].update(next_current_states)
                    else:
                        state_transition_dict[input_symbol] = next_current_states

            if (new_final_states & lambda_enclosure):
                new_final_states.add(state)

            if state in new_transitions:
                new_transitions[state].pop('', None)

        # Remove unreachable states
        reachable_states = NFA._compute_reachable_states(self.initial_state, self.input_symbols, new_transitions)
        reachable_final_states = reachable_states & new_final_states

        for state in self.states - reachable_states:
            new_transitions.pop(state, None)

        return reachable_states, new_transitions, reachable_final_states

    def eliminate_lambda(self):
        """Removes epsilon transitions from the NFA which recognizes the same language."""

        reachable_states, new_transitions, reachable_final_states = self._eliminate_lambda()

        return self.__class__(
            states=reachable_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=reachable_final_states
        )

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
        current_states = self._lambda_closures[self.initial_state]

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

        state_name_counter = count(start)

        state_map_a = dict(zip(state_set_a, state_name_counter))
        state_map_b = dict(zip(state_set_b, state_name_counter))

        return (state_map_a, state_map_b)

    def union(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the union of L1 and L2.
        """

        # Starting at 1 because 0 is for the initial state
        (state_map_a, state_map_b) = NFA._get_state_maps(self.states, other.states, start=1)

        new_states = frozenset(chain(state_map_a.values(), state_map_b.values(), [0]))
        new_transitions = {state: {} for state in new_states}

        # Connect new initial state to both branch
        new_transitions[0] = {'': {state_map_a[self.initial_state], state_map_b[other.initial_state]}}

        # Transitions of self
        NFA._load_new_transition_dict(state_map_a, self.transitions, new_transitions)
        # Transitions of other
        NFA._load_new_transition_dict(state_map_b, other.transitions, new_transitions)

        # Final states
        new_final_states = frozenset(chain(
            (state_map_a[state] for state in self.final_states),
            (state_map_b[state] for state in other.final_states)
        ))

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

        new_states = frozenset(chain(state_map_a.values(), state_map_b.values()))
        new_transitions = {state: {} for state in new_states}

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
        new_final_states = frozenset(state_map_b[state] for state in other.final_states)

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
        new_transitions = dict(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {
            '': {self.initial_state}
        }
        # For each final state in original NFA we add epsilon
        # transition to the old initial state
        for state in self.final_states:
            new_transitions[state] = dict(new_transitions.get(state, {}))
            transition = new_transitions[state]
            transition[''] = set(transition.get('', set()))
            transition[''].add(self.initial_state)

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
        new_transitions = dict(self.transitions)
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
            state: {} for state in new_states
        }

        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                for state_b in states:
                    new_transitions[state_b].setdefault(symbol, set()).add(state_a)

        # And we additionally have epsilon transitions from
        # new initial state to each old final state.
        new_transitions[new_initial_state][''] = set(self.final_states)
        new_final_states = {self.initial_state}

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def intersection(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the intersection of L1 and L2.
        """

        new_states = set()
        new_input_symbols = self.input_symbols | other.input_symbols
        new_transitions = {}
        new_initial_state = (self.initial_state, other.initial_state)

        queue = deque()

        queue.append(new_initial_state)
        new_states.add(new_initial_state)

        while queue:
            curr_state = queue.popleft()
            q_a, q_b = curr_state

            # States we will consider adding to the queue
            next_states_iterables = list()

            # Get transition dict for states in self
            transitions_a = self.transitions.get(q_a, {})
            # Add epsilon transitions for first set of transitions
            epsilon_transitions_a = transitions_a.get('')
            if epsilon_transitions_a is not None:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault('', set()).update(product(epsilon_transitions_a, [q_b]))
                next_states_iterables.append(product(epsilon_transitions_a, [q_b]))

            # Get transition dict for states in other
            transitions_b = other.transitions.get(q_b, {})
            # Add epsilon transitions for second set of transitions
            epsilon_transitions_b = transitions_b.get('')
            if epsilon_transitions_b is not None:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault('', set()).update(product([q_a], epsilon_transitions_b))
                next_states_iterables.append(product([q_a], epsilon_transitions_b))

            # Add all transitions moving over same input symbols
            for symbol in new_input_symbols:
                end_states_a = transitions_a.get(symbol)
                end_states_b = transitions_b.get(symbol)

                if end_states_a is not None and end_states_b is not None:
                    state_dict = new_transitions.setdefault(curr_state, {})
                    state_dict.setdefault(symbol, set()).update(product(end_states_a, end_states_b))
                    next_states_iterables.append(product(end_states_a, end_states_b))

            # Finally, try visiting every state we found.
            for product_state in chain.from_iterable(next_states_iterables):
                if product_state not in new_states:
                    new_states.add(product_state)
                    queue.append(product_state)

        new_final_states = frozenset(
            (state_a, state_b)
            for (state_a, state_b) in new_states
            if state_a in self.final_states and state_b in other.final_states
        )

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def shuffle_product(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the shuffle of L1 and L2.
        """
        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state)
        new_states = frozenset(product(self.states, other.states))

        new_transitions = {}

        for curr_state in new_states:
            state_dict = new_transitions.setdefault(curr_state, {})
            q_a, q_b = curr_state

            transitions_a = self.transitions.get(q_a, {})
            for symbol, end_states in transitions_a.items():
                state_dict.setdefault(symbol, set()).update(product(end_states, [q_b]))

            transitions_b = other.transitions.get(q_b, {})
            for symbol, end_states in transitions_b.items():
                state_dict.setdefault(symbol, set()).update(product([q_a], end_states))

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=frozenset(product(self.final_states, other.final_states))
        )

    def right_quotient(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the right quotient of L1 with respect to L2 (L1 / L2).

        Construction is based off of the one described here:
        https://cs.stackexchange.com/a/102043
        """

        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        # First, eliminate lambdas because they cause problems with this algorithm
        self_reachable_states, self_new_transitions, self_reachable_final_states = self._eliminate_lambda()
        other_reachable_states, other_new_transitions, other_reachable_final_states = other._eliminate_lambda()

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state, False)
        new_final_states = frozenset(product(self_reachable_final_states, other_reachable_final_states, [True]))
        new_states = frozenset(chain(
            product(self_reachable_states, [other.initial_state], [False]),
            product(self_reachable_states, other_reachable_states, [True])
        ))

        new_transitions = {}

        # Populate transitions for before reading the suffix
        for state in self_reachable_states:
            new_state = (state, other.initial_state, False)
            new_state_dict = new_transitions.setdefault(new_state, {})
            old_transitions_dict = self_new_transitions.get(state)

            if old_transitions_dict:
                for symbol, end_states in old_transitions_dict.items():
                    new_state_dict[symbol] = {
                        (end_state, other.initial_state, False)
                        for end_state in end_states
                    }

            new_state_dict[''] = {(state, other.initial_state, True)}

        # Start reading after the suffix
        for q_a, q_b in product(self_reachable_states, other_reachable_states):
            curr_state = (q_a, q_b, True)

            transitions_a = self_new_transitions.get(q_a, {})
            transitions_b = other_new_transitions.get(q_b, {})

            # Add all transitions moving over same input symbols
            for symbol in new_input_symbols:
                end_states_a = transitions_a.get(symbol)
                end_states_b = transitions_b.get(symbol)

                if end_states_a is not None and end_states_b is not None:
                    state_dict = new_transitions.setdefault(curr_state, {})
                    state_dict.setdefault('', set()).update(product(end_states_a, end_states_b, [True]))

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states
        )

    def left_quotient(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the left quotient of L1 with respect to L2 (L2 \\ L1).

        Construction is based off of the one described here:
        https://cs.stackexchange.com/a/102043
        """

        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        # First, eliminate lambdas because they cause problems with this algorithm
        self_reachable_states, self_new_transitions, self_reachable_final_states = self._eliminate_lambda()
        other_reachable_states, other_new_transitions, other_reachable_final_states = other._eliminate_lambda()

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state, False)
        new_final_states = frozenset(product(self_reachable_final_states, other_reachable_final_states, [True]))
        new_states = frozenset(chain(
            product(self_reachable_states, other_reachable_states, [False]),
            product(self_reachable_states, other_reachable_final_states, [True])
        ))

        new_transitions = {}

        # Start reading the prefix
        for q_a, q_b in product(self_reachable_states, other_reachable_states):
            curr_state = (q_a, q_b, False)

            transitions_a = self_new_transitions.get(q_a, {})
            transitions_b = other_new_transitions.get(q_b, {})

            # Add all transitions moving over same input symbols
            for symbol in new_input_symbols:
                end_states_a = transitions_a.get(symbol)
                end_states_b = transitions_b.get(symbol)

                if end_states_a is not None and end_states_b is not None:
                    state_dict = new_transitions.setdefault(curr_state, {})
                    state_dict.setdefault('', set()).update(product(end_states_a, end_states_b, [False]))

            # Add lambda transition from final state, flipping third entry to true
            if q_b in other_reachable_final_states:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault('', set()).add((q_a, q_b, True))

        # Populate transitions for after reading the prefix
        for state_a, state_b in product(self_reachable_states, other_reachable_final_states):
            new_state = (state_a, state_b, True)
            new_state_dict = new_transitions.setdefault(new_state, {})
            old_transitions_dict = self_new_transitions.get(state_a)

            if old_transitions_dict:
                for symbol, end_states in old_transitions_dict.items():
                    new_state_dict[symbol] = {
                        (end_state, state_b, True)
                        for end_state in end_states
                    }

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
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

    def __eq__(self, other):
        """
        Return True if two NFAs are equivalent. Uses an optimized version of
        the extended Hopcroft-Karp algorithm (HKe). See
        https://arxiv.org/abs/0907.5058
        """

        # Must be another NFA and have equal alphabets
        if not isinstance(other, NFA) or self.input_symbols != other.input_symbols:
            return NotImplemented

        operand_nfas = (self, other)
        initial_state_a = (self._lambda_closures[self.initial_state], 0)
        initial_state_b = (other._lambda_closures[other.initial_state], 1)

        def is_final_state(states_pair):
            states, operand_index = states_pair
            nfa = operand_nfas[operand_index]
            # If at least one of the current states is a final state, the
            # condition should satisfy
            return any(
                len(nfa.final_states & nfa._lambda_closures[state]) > 0
                for state in states
            )

        def transition(states_pair, symbol):
            states, operand_index = states_pair
            return (
                operand_nfas[operand_index]._get_next_current_states(
                    states, symbol),
                operand_index
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

    @classmethod
    def edit_distance(cls, input_symbols, reference_str, max_edit_distance, *,
                      insertion=True, deletion=True, substitution=True):
        """
        Constructs the Levenshtein NFA for the given reference_str and
        given Levenshtein distance. This NFA recognizes strings within the given
        Levenshtein distance (commonly called edit distance) of the reference_str.
        Parameters control which error types the NFA will recognize (insertions,
        deletions, or substitutions). At least one error type must be set.

        If insertion and deletion are False and substitution is True,
        then this is the same as Hamming distance.

        If insertion and deletion are True and substitution is False,
        then this is the same as LCS distance.

        insertion, deletion, and substitution all default to True.

        Code adapted from: http://blog.notdot.net/2010/07/Damn-Cool-Algorithms-Levenshtein-Automata
        """
        if max_edit_distance < 0:
            raise ValueError("max_edit_distance must be greater than zero")
        if not (insertion or deletion or substitution):
            raise ValueError("At least one of insertion, deletion, or substitution must be enabled.")

        states = frozenset(product(range(len(reference_str)+1), range(max_edit_distance+1)))

        transitions = {}
        final_states = set()

        def add_transition(start_state_dict, end_state, symbol):
            """Add transition between start and end state on symbol"""
            start_state_dict.setdefault(symbol, set()).add(end_state)

        def add_any_transition(start_state_dict, end_state):
            """Add transition on all symbols between start and end state"""
            for symbol in input_symbols:
                add_transition(start_state_dict, end_state, symbol)

        for (i, chr), e in product(enumerate(reference_str), range(max_edit_distance + 1)):
            state_transition_dict = transitions.setdefault((i, e), {})

            # Correct character
            add_transition(state_transition_dict, (i + 1, e), chr)
            if e < max_edit_distance:
                if insertion:
                    # Insertion
                    add_any_transition(state_transition_dict, (i, e + 1))

                if deletion:
                    # Deletion
                    add_transition(state_transition_dict, (i + 1, e + 1), '')

                if substitution:
                    # Substitution
                    add_any_transition(state_transition_dict, (i + 1, e + 1))

        for e in range(max_edit_distance + 1):
            state_transition_dict = transitions.setdefault((len(reference_str), e), {})
            if insertion and e < max_edit_distance:
                add_any_transition(state_transition_dict, (len(reference_str), e + 1))

            final_states.add((len(reference_str), e))

        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=(0, 0),
            final_states=final_states
        )
