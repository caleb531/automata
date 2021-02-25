#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
import itertools
from collections import deque

import automata.base.exceptions as exceptions
import automata.fa.fa as fa

from graphviz import Digraph


class DFA(fa.FA):
    """A deterministic finite automaton."""

    def __init__(self, *, states, input_symbols, transitions,
                 initial_state, final_states):
        """Initialize a complete DFA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.validate()

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

    def minify(self, retain_names=True):
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
            for symbol, dst_state in self.transitions[state].items():
                if dst_state not in reachable_states:
                    reachable_states.add(dst_state)
                    states_to_check.append(dst_state)
        return reachable_states

    def _merge_states(self, retain_names=True):
        eq_classes = []
        if len(self.final_states) != 0:
            eq_classes.append(frozenset(self.final_states))
        if len(self.final_states) != len(self.states):
            eq_classes.append(
                frozenset(set(self.states).difference(self.final_states))
            )
        eq_classes = set(eq_classes)

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
        eq_classes = list(eq_classes)

        def rename(eq):
            return list(eq)[0] if len(eq) == 1 else DFA._stringify_states(eq)

        # need a backmap to prevent constant calls to index
        back_map = {}
        for i, eq in enumerate(eq_classes):
            name = rename(eq) if retain_names else i
            for state in eq:
                back_map[state] = name

        new_input_symbols = self.input_symbols
        new_states = ({rename(eq) for eq in eq_classes} if retain_names
                      else set(range(len(eq_classes))))
        new_initial_state = back_map[self.initial_state]
        new_final_states = set([back_map[acc] for acc in self.final_states])
        new_transitions = {}
        for i, eq in enumerate(eq_classes):
            name = rename(eq) if retain_names else i
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

    @staticmethod
    def _stringify_states(states):
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(','.join(sorted(states)))

    @classmethod
    def _add_nfa_states_from_queue(cls, nfa, current_states,
                                   current_state_name, dfa_states,
                                   dfa_transitions, dfa_final_states):
        """Add NFA states to DFA as it is constructed from NFA."""
        dfa_states.add(current_state_name)
        dfa_transitions[current_state_name] = {}
        if (current_states & nfa.final_states):
            dfa_final_states.add(current_state_name)

    @classmethod
    def _enqueue_next_nfa_current_states(cls, nfa, current_states,
                                         current_state_name, state_queue,
                                         dfa_transitions):
        """Enqueue the next set of current states for the generated DFA."""
        for input_symbol in nfa.input_symbols:
            next_current_states = nfa._get_next_current_states(
                current_states, input_symbol)
            dfa_transitions[current_state_name][input_symbol] = (
                cls._stringify_states(next_current_states))
            state_queue.append(next_current_states)

    @classmethod
    def from_nfa(cls, nfa):
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states = set()
        dfa_symbols = nfa.input_symbols
        dfa_transitions = {}
        # equivalent DFA states states
        nfa_initial_states = nfa._get_lambda_closure(nfa.initial_state)
        dfa_initial_state = cls._stringify_states(nfa_initial_states)
        dfa_final_states = set()

        state_queue = deque()
        state_queue.append(nfa_initial_states)
        while state_queue:

            current_states = state_queue.popleft()
            current_state_name = cls._stringify_states(current_states)
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

    def show_diagram(
        self,
        filename: str = None,
        format_type: str = 'png',
        path: str = None,
        horizontal: bool = True,
        reverse_orientation: bool = False,
        fig_size: tuple = (8, 8),
        font_size: float = 14,
        arrow_size: float = 0.85,
        state_seperation: float = 0.5,
    ):
        """
        Creates the graph associated with this self
        """
        # Nodes are set of states.

        # Converting to graphviz preferred input type,
        # keeping the conventional input styles; i.e fig_size(8,8)
        fig_size = ', '.join(map(str, fig_size))
        font_size = str(font_size)
        arrow_size = str(arrow_size)
        state_seperation = str(state_seperation)

        # Defining the graph.
        graph = Digraph(strict=False)
        graph.attr(
            size=fig_size,
            ranksep=state_seperation,
        )
        if horizontal:
            graph.attr(rankdir='LR')
        if reverse_orientation:
            if horizontal:
                graph.attr(rankdir='RL')
            else:
                graph.attr(rankdir='BT')

        # Defining arrow to indicate the initial state.
        graph.node('Initial', label='', shape='point', fontsize=font_size)

        # Defining all states.
        for state in sorted(self.states):
            if state in self.initial_state:
                graph.node(state, shape='circle', fontsize=font_size)
            elif state in self.final_states:
                graph.node(state, shape='doublecircle', fontsize=font_size)
            else:
                graph.node(state, shape='circle', fontsize=font_size)

        # Point initial arrow to the initial state.
        graph.edge('Initial', self.initial_state, arrowsize=arrow_size)

        # Define all tansitions in the finite state machine.
        for symbol in sorted(self.input_symbols):
            for k, v in self.transitions.items():
                graph.edge(
                    k,
                    v[symbol],
                    label=' {} '.format(symbol),
                    arrowsize=arrow_size,
                    fontsize=font_size,
                )

        # Write diagram to file. PNG, SVG, etc.
        if filename:
            graph.render(
                filename=filename,
                format=format_type,
                directory=path,
                cleanup=True
            )
        return graph
