#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""

import copy

import automata.base.exceptions as exceptions
import automata.fa.fa as fa

from graphviz import Digraph


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

        # Replacing '' the key name for empty string (lambda/epsilon) transitions.
        transitions = self.transitions
        input_symbols = self.input_symbols
        for k, v in transitions.items():
            for sub_k, sub_v in list(v.items()):
                if sub_k == '':
                    v['λ'] = sub_v
                    del v['']
                    input_symbols.add('λ')

        # Define all tansitions in the finite state machine.
        for symbol in sorted(input_symbols):
            for k, v in transitions.items():
                if symbol in v:
                    for v_n in v[symbol]:
                        graph.edge(
                            k,
                            v_n,
                            label=' {} '.format(symbol),
                            arrowsize=arrow_size,
                            fontsize=font_size,
                        )

        # Write diagram to file. PNG, SVG, etc.
        if filename:
            graph.render(
                filename=filename, format=format_type, directory=path, cleanup=True
            )
        return graph
