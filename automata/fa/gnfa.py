#!/usr/bin/env python3
"""Classes and methods for working with generalized non-deterministic finite automata."""

import copy
from abc import ABC

from pydot import Dot, Edge, Node

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
from automata.base.regex import RegEx as re


class GNFA(fa.FA):
    """A generalized nondeterministic finite automaton."""

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_state):
        """Initialize a complete NFA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_state = final_state
        self.validate()

    @classmethod
    def from_dfa(cls, dfa):
        """Initialize this GNFA as one equivalent to the given DFA."""
        gnfa = dfa.copy()

        for state in gnfa.states:
            gnfa_transitions = dict()
            for input_symbol, to_state in gnfa.transitions[state].items():
                if to_state in gnfa_transitions.keys():
                    gnfa_transitions[to_state] = "{}|{}".format(gnfa_transitions[to_state], input_symbol)
                else:
                    gnfa_transitions[to_state] = input_symbol
            gnfa.transitions[state] = gnfa_transitions

        gnfa.states.add(0)  # add new start state
        gnfa.transitions[0] = {gnfa.initial_state: ''}
        gnfa.initial_state = 0
        gnfa.states.add(1)  # add new accept state

        for state in gnfa.final_states:
            gnfa.transitions[state][1] = ''
        gnfa.final_state = 1

        for state in gnfa.states - {1}:
            if gnfa.states - gnfa.transitions[state].keys():
                for leftover_state in gnfa.states - gnfa.transitions[state].keys():
                    if leftover_state is not gnfa.initial_state:
                        gnfa.transitions[state][leftover_state] = None

        return cls(
            states=gnfa.states, input_symbols=gnfa.input_symbols,
            transitions=gnfa.transitions, initial_state=gnfa.initial_state,
            final_state=gnfa.final_state)

    @classmethod
    def from_nfa(cls, nfa):
        """Initialize this GNFA as one equivalent to the given NFA."""
        gnfa = nfa.copy()

        for state in gnfa.states:
            gnfa_transitions = dict()
            for input_symbol, to_states in gnfa.transitions[state].items():
                for to_state in to_states:
                    if to_state in gnfa_transitions.keys():
                        if gnfa_transitions[to_state] == '' or input_symbol == '':
                            gnfa_transitions[to_state] = ''
                        else:
                            gnfa_transitions[to_state] = "{}|{}".format(gnfa_transitions[to_state], input_symbol)
                    else:
                        gnfa_transitions[to_state] = input_symbol
            gnfa.transitions[state] = gnfa_transitions

        gnfa.states.add(0)  # add new start state
        gnfa.transitions[0] = {gnfa.initial_state: ''}
        gnfa.initial_state = 0
        gnfa.states.add(1)  # add new accept state

        for state in gnfa.final_states:
            gnfa.transitions[state][1] = ''
        gnfa.final_state = 1

        for state in gnfa.states - {1}:
            if gnfa.states - gnfa.transitions[state].keys():
                for leftover_state in gnfa.states - gnfa.transitions[state].keys():
                    if leftover_state is not gnfa.initial_state:
                        gnfa.transitions[state][leftover_state] = None

        return cls(
            states=gnfa.states, input_symbols=gnfa.input_symbols,
            transitions=gnfa.transitions, initial_state=gnfa.initial_state,
            final_state=gnfa.final_state)

    @staticmethod
    def _validate_regex(regex):
        """Return True if the regular expression is valid"""

        stack1 = 0
        for i in range(len(regex)):
            if regex[i] == '(':
                stack1 += 1
            elif regex[i] == ')':
                stack1 = stack1 - 1

            if stack1 < 0:
                return False

            if regex[i] == '*':
                if i > 0 and regex[i-1] in {'(', '|', '*'}:
                    return False
                elif i == 0:
                    return False

            if regex[i] == '|':
                if i > 1 and regex[i-1] in {'(', '|'}:
                    return False
                elif i < len(regex)-1 and regex[i+1] in {')', '|', '*'}:
                    return False
                elif i == 0 or i == len(regex)-1:
                    return False

            if regex[i] == '(':
                if i < len(regex)-1 and regex[i+1] == ')':
                    return False
        if stack1 != 0:
            return False
        else:
            return True

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition symbols are invalid."""
        for regex in paths.values():
            check = self.input_symbols.copy()
            check = check.union({'*', '|', '(', ')'})
            if regex is not None and (set(regex) - check and regex != '' or not self._validate_regex(regex)):
                raise exceptions.InvalidSymbolError(
                    'state {} has invalid transition expression {}'.format(
                        start_state, regex))

    def _validate_transition_end_states(self, start_state, paths):
        """Raise an error if transition end states are invalid."""
        for end_state in paths.keys():
                if end_state not in self.states:
                    raise exceptions.InvalidStateError(
                        'end state {} for transition on {} is '
                        'not valid'.format(end_state, start_state))

    def _validate_final_state(self):
        """Raise an error if the initial state is invalid."""
        if self.final_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} is not a valid final state'.format(self.final_state))

    def validate(self):
        """Return True if this NFA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
            self._validate_transition_end_states(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_final_state()
        return True

    def _isbracket_req(self, regex):
        bracket_open = 0
        for i in range(len(regex)):
            if regex[i] == '(':
                bracket_open += 1
            elif regex[i] == ')':
                bracket_open = bracket_open - 1
            if bracket_open == 0 and regex[i] == '|':
                return True
            else:
                return False

    @staticmethod
    def _find_min_connected_node(gnfa):
        state_set = gnfa.states-{gnfa.initial_state, gnfa.final_state}
        state_degree = dict.fromkeys(state_set, 0)
        for state in gnfa.states - {gnfa.final_state}:
            for to_state, label in gnfa.transitions[state].items():
                if label is not None:
                    if state != gnfa.initial_state:
                        state_degree[state] = state_degree[state] + 1
                    if to_state != gnfa.final_state:
                        state_degree[to_state] = state_degree[to_state] + 1

        return min(state_degree, key=state_degree.get)

    def _to_regex(self, gnfa):
        """
        Convert GNFA to regular expression.
        Helper function for 'to_regex' function.
        """
        k = len(gnfa.states)
        if k == 2:
            return gnfa.transitions[gnfa.initial_state][gnfa.final_state]
        else:
            q_rip = self._find_min_connected_node(gnfa)
            new_states = gnfa.states - {q_rip}
            for q_i in new_states - {gnfa.final_state}:
                for q_j in new_states - {gnfa.initial_state}:
                    r1 = gnfa.transitions[q_i][q_rip]
                    r2 = gnfa.transitions[q_rip][q_rip]
                    r3 = gnfa.transitions[q_rip][q_j]
                    r4 = gnfa.transitions[q_i][q_j]

                    if r1 is None or r3 is None:
                        gnfa.transitions[q_i][q_j] = r4
                    else:
                        # check if putting brackets around r1 is necessary
                        if self._isbracket_req(r1):
                            r1 = '({})'.format(r1)

                        if r2 is None:
                            r2 = ''
                        elif len(r2) == 2 and r2[1] == '*':
                            pass
                        elif len(r2) > 1:
                            r2 = '({})*'.format(r2)
                        elif len(r2) == 1:
                            r2 = '{}*'.format(r2)

                        if self._isbracket_req(r3):
                            r3 = '({})'.format(r3)

                        if r4 is None:
                            r4 = ''
                        elif self._isbracket_req(r4):
                            r4 = '|({})'.format(r2)
                        else:
                            r4 = '|{}'.format(r4)

                        gnfa.transitions[q_i][q_j] = r1 + r2 + r3 + r4
            gnfa.states = new_states
            del gnfa.transitions[q_rip]
            for state in gnfa.states-{gnfa.final_state}:
                del gnfa.transitions[state][q_rip]

            return self._to_regex(gnfa)

    def to_regex(self):
        gnfa = self.copy()
        return self._to_regex(gnfa)

    def show_diagram(self, path=None, show_None = True):
        """
            Creates the graph associated with this DFA
        """
        # Nodes are set of states

        graph = Dot(graph_type='digraph', rankdir='LR')
        nodes = {}
        for state in self.states:
            if state == self.initial_state:
                # color start state with green
                initial_state_node = Node(
                    state, style='filled', fillcolor='#66cc33')
                nodes[state] = initial_state_node
                graph.add_node(initial_state_node)
            else:
                if state == self.final_state:
                    state_node = Node(state, peripheries=2)
                else:
                    state_node = Node(state)
                nodes[state] = state_node
                graph.add_node(state_node)
        # adding edges
        for from_state, lookup in self.transitions.items():
            for to_state, to_label in lookup.items():
                if to_label is None and show_None:
                    to_label = "ø"
                    graph.add_edge(Edge(
                        nodes[from_state],
                        nodes[to_state],
                        label=to_label
                    ))
                elif to_label is not None:
                    graph.add_edge(Edge(
                        nodes[from_state],
                        nodes[to_state],
                        label=to_label
                    ))
        if path:
            graph.write_png(path)
        return graph

    def read_input_stepwise(self, input_str):
        """This method is not implemented yet in GNFA, wait for future versions"""

        pass


