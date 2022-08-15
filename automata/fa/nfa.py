#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""

import copy
from collections import deque

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.fa.dfa import DFA

from pydot import Dot, Edge, Node


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

    @classmethod
    def _from_symbol(cls, symbol, input_symbols=None):
        """Generate NFA from single symbol, `input symbols` may be passed to initialize input_symbols for NFA"""
        states = {0, 1}
        initial_state = 0
        if input_symbols is None:
            input_symbols = {symbol}
        transitions = {0: {symbol: {1}}}
        final_states = {1}

        return NFA(
            states=states,
            input_symbols=input_symbols,
            initial_state=initial_state,
            transitions=transitions,
            final_states=final_states
        )

    @staticmethod
    def _kleene_star(master_list):
        """Helper function for from_regex. applies kleene star operation wherever possible."""
        i = 0
        while True:
            if i == len(master_list) - 1:
                break
            elif not isinstance(master_list[i], NFA):
                i += 1
            elif i != len(master_list) - 1 and not isinstance(master_list[i + 1], NFA) and master_list[i + 1] == '*':
                master_list[i] = master_list[i].kleene_star()
                master_list.pop(i + 1)
            else:
                i += 1

    @staticmethod
    def _option(master):
        """applies ? operator wherever possible in master list"""
        i = 0
        while True:
            if i == len(master) - 1:
                break
            elif not isinstance(master[i], NFA):
                i += 1
            elif i != len(master) - 1 and not isinstance(master[i + 1], NFA) and master[i + 1] == '?':
                master[i] = master[i].option()
                master.pop(i + 1)
            else:
                i += 1

    @staticmethod
    def _concatenate(master_list):
        """applies concatenation operator wherever possible"""
        i = 0
        while True:
            if i == len(master_list) - 1:
                break
            elif not isinstance(master_list[i], NFA):
                i += 1
            elif i != len(master_list) - 1 and isinstance(master_list[i + 1], NFA):
                master_list[i] = master_list[i].concatenate(master_list[i + 1])
                master_list.pop(i + 1)
            else:
                i += 1

    @staticmethod
    def _union(master):
        """applies union operation wherever possible in master list"""
        # apply union in the highest level of parenthesis only

        bracket_level = 0
        highest_bracket = None
        for i in range(len(master)):  # pragma: no branch
            if not isinstance(master[i], NFA):
                if master[i] == '|':
                    if highest_bracket is None or highest_bracket < bracket_level:
                        highest_bracket = bracket_level
                elif master[i] == '(':
                    bracket_level += 1
                elif master[i] == ')':  # pragma: no branch
                    bracket_level -= 1

        if highest_bracket is None:
            return

        stack = 0
        i = 0
        while True:
            if i == len(master) - 1:
                break
            elif not isinstance(master[i], NFA) and master[i] == '(':
                stack += 1
                i += 1
            elif not isinstance(master[i], NFA) and master[i] == ')':
                stack = stack - 1
                i += 1
            elif stack == highest_bracket and not isinstance(master[i], NFA) and master[i] == '|' \
                    and isinstance(master[i + 1], NFA) \
                    and isinstance(master[i - 1], NFA):
                master[i - 1] = master[i - 1].union(master[i + 1])
                master.pop(i)
                master.pop(i)
                i = i - 1
            else:
                i += 1

    @staticmethod
    def _remove_excess_parenthesis(master):
        """removes excess parenthesis from the master list"""
        i = 0
        while True:
            if i == len(master) - 1:
                break
            elif i != 0 and i != len(master) - 1 \
                    and isinstance(master[i], NFA) \
                    and not isinstance(master[i - 1], NFA) and master[i - 1] == '(' \
                    and not isinstance(master[i + 1], NFA) and master[i + 1] == ')':
                master.pop(i - 1)
                master.pop(i)
                i = i - 1
            else:
                i += 1

    @classmethod
    def from_regex(cls, regex):
        """Initialize this NFA as one equivalent to the given regular expression"""

        if regex == '':
            return NFA(
                states={0},
                initial_state=0,
                final_states={0},
                transitions={},
                input_symbols=set()
            )

        cls._validate_regex(regex)
        symbols = set(regex) - {'*', '|', '(', ')', '?'}
        master = list(regex)
        for i in range(len(master)):
            if master[i] in symbols:
                master[i] = cls._from_symbol(master[i], symbols)

        def star_and_option():
            initial_length = len(master)
            while True:
                cls._kleene_star(master)
                cls._option(master)
                cls._remove_excess_parenthesis(master)
                if len(master) < initial_length:
                    initial_length = len(master)
                else:
                    break

        def star_option_concatenate():
            initial_length = len(master)
            while True:
                star_and_option()
                cls._concatenate(master)
                cls._remove_excess_parenthesis(master)
                if len(master) < initial_length:
                    initial_length = len(master)
                else:
                    break

        def star_option_concatenate_union():
            initial_length = len(master)
            while True:
                star_option_concatenate()
                cls._union(master)
                cls._remove_excess_parenthesis(master)
                if len(master) == 1:
                    break

        star_option_concatenate_union()
        return master[0]

    def _validate_transition_end_states(self, start_state, paths):
        """Raise an error if transition end states are invalid."""
        for end_states in paths.values():
            for end_state in end_states:
                if end_state not in self.states:
                    raise exceptions.InvalidStateError(
                        'end state {} for transition on {} is '
                        'not valid'.format(end_state, start_state))

    @staticmethod
    def _validate_regex(regex):
        """Return True if the regular expression is valid"""

        result = True
        stack1 = 0
        for i in range(len(regex)):
            if regex[i] == '(':
                stack1 += 1
            elif regex[i] == ')':
                stack1 = stack1 - 1

            if stack1 < 0:
                result = False

            if regex[i] == '*':
                if i > 0 and regex[i - 1] in {'(', '|', '*', '?'}:
                    result = False
                elif i == 0:
                    result = False

            if regex[i] == '|':
                if i > 1 and regex[i - 1] in {'(', '|'}:
                    result = False
                elif i < len(regex) - 1 and regex[i + 1] in {')', '|', '*', '?'}:
                    result = False
                elif i == 0 or i == len(regex) - 1:
                    result = False

            if regex[i] == '(':
                if i < len(regex) - 1 and regex[i + 1] == ')':
                    result = False

            if i == 0 and regex[i] == '?':
                result = False
        if stack1 != 0:
            result = False

        if not result:
            raise exceptions.InvalidRegexError(
                '{} is an invalid regular expression'.format(
                    regex))

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
                if state in self.transitions and '' in self.transitions[state]:
                    stack.extend(self.transitions[state][''])

        return encountered_states

    def _get_next_current_states(self, current_states, input_symbol):
        """Return the next set of current states given the current set."""
        next_current_states = set()

        for current_state in current_states:
            if current_state in self.transitions:
                symbol_end_states = self.transitions[current_state].get(
                    input_symbol)
                if symbol_end_states:
                    for end_state in symbol_end_states:
                        next_current_states.update(
                            self._get_lambda_closure(end_state))

        return next_current_states

    def _get_next_current_states2(self, current_states, input_symbol):
        """Return the next set of current states given the current set."""
        next_current_states = set()

        for current_state in current_states:
            if current_state in self.transitions:
                symbol_end_states = self.transitions[current_state].get(
                    input_symbol)
                if symbol_end_states:
                    next_current_states.update(symbol_end_states)

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
        reachable_states = set()
        states_to_check = deque()
        states_to_check.append(self.initial_state)
        reachable_states.add(self.initial_state)
        while states_to_check:
            state = states_to_check.popleft()
            for symbol, dst_states in self.transitions[state].items():
                for dst_state in dst_states:
                    if dst_state not in reachable_states:
                        reachable_states.add(dst_state)
                        states_to_check.append(dst_state)
        return reachable_states

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
            lambda_enclosure = self._get_lambda_closure(state) - {state}
            for input_symbol in self.input_symbols:
                next_current_states = self._get_next_current_states2(lambda_enclosure, input_symbol)
                if state not in self.transitions:
                    self.transitions[state] = dict()
                if input_symbol in self.transitions[state]:
                    self.transitions[state][input_symbol].update(next_current_states)
                else:
                    self.transitions[state][input_symbol] = next_current_states

            if state not in self.final_states and self.final_states & lambda_enclosure:
                self.final_states.add(state)
            self.transitions[state].pop('', None)

        self._remove_unreachable_states()
        self._remove_empty_transitions()

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

    def union(self, other):
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the union of L1 and L2.
        """
        if not isinstance(other, NFA):
            raise NotImplementedError

        # first check superset or subset relation
        if DFA.from_nfa(self).issubset(DFA.from_nfa(other)):
            return other.copy()
        elif DFA.from_nfa(self).issuperset(DFA.from_nfa(other)):
            return self.copy()

        state_map_a = dict()
        for state in self.states:
            state_map_a[state] = len(state_map_a) + 1

        state_map_b = dict()
        for state in other.states:
            state_map_b[state] = len(state_map_a) + len(state_map_b) + 1

        new_states = set(state_map_a.values()) | set(state_map_b.values()) | {0}
        new_transitions = dict()
        for state in new_states:
            new_transitions[state] = dict()

        # Connect new initial state to both branch
        new_transitions[0] = {'': {state_map_a[self.initial_state], state_map_b[other.initial_state]}}
        # Transitions of self
        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                new_transitions[state_map_a[state_a]][symbol] = {
                    state_map_a[state_b] for state_b in states
                }

        # Transitions of other
        for state_a, transitions in other.transitions.items():
            for symbol, states in transitions.items():
                new_transitions[state_map_b[state_a]][symbol] = {
                    state_map_b[state_b] for state_b in states
                }

        # Final states
        new_final_states = {state_map_a[state] for state in self.final_states} | {state_map_b[state] for state in
                                                                                  other.final_states}

        return NFA(
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
        new_states.add(new_initial_state)

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

        return NFA(
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
        new_initial_state = 0
        while new_initial_state in self.states:
            new_initial_state += 1
        new_states.add(new_initial_state)

        # Transitions are the same with a few additions.
        new_transitions = copy.deepcopy(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {
            '': {self.initial_state}
        }

        return NFA(
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
