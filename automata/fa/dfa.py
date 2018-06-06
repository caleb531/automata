#!/usr/bin/env python3
"""Classes and methods for working with deterministic finite automata."""

import copy
import itertools
import queue

import automata.base.exceptions as exceptions
import automata.fa.fa as fa


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

    def minify(self):
        """
        Create a minimal DFA which accepts the same inputs as this DFA.

        First, non-reachable states are removed.
        Then, similiar states are merged.
        """
        new_dfa = self.copy()
        new_dfa._remove_unreachable_states()
        states_table = new_dfa._create_markable_states_table()
        new_dfa._mark_states_table_first(states_table)
        new_dfa._mark_states_table_second(states_table)
        new_dfa._join_non_marked_states(states_table)
        return new_dfa

    def _remove_unreachable_states(self):
        """Remove states which are not reachable from the initial state."""
        reachable_states = self._compute_reachable_states()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transitions[state]

    def _compute_reachable_states(self):
        """Compute the states which are reachable from the initial state."""
        reachable_states = set()
        states_to_check = queue.Queue()
        states_checked = set()
        states_to_check.put(self.initial_state)
        while not states_to_check.empty():
            state = states_to_check.get()
            reachable_states.add(state)
            for symbol, dst_state in self.transitions[state].items():
                if dst_state not in states_checked:
                    states_to_check.put(dst_state)
            states_checked.add(state)
        return reachable_states

    def _create_markable_states_table(self):
        """
        Create a "markable table" with all combinatations of two states.

        This is a dict with frozensets of states as keys and `False` as value.
        """
        table = {
            frozenset(c): False
            for c in itertools.combinations(self.states, 2)
        }
        return table

    def _mark_states_table_first(self, table):
        """Mark pairs of states if one is final and one is not."""
        for s in table.keys():
            if any((x in self.final_states for x in s)):
                if any((x not in self.final_states for x in s)):
                    table[s] = True

    def _mark_states_table_second(self, table):
        """
        Mark additional state pairs.

        A non-marked pair of two states q, q_ will be marked
        if there is an input_symbol a for which the pair
        transition(q, a), transition(q_, a) is marked.
        """
        changed = True
        while changed:
            changed = False
            for s in filter(lambda s: not table[s], table.keys()):
                s_ = tuple(s)
                for a in self.input_symbols:
                    s2 = frozenset({
                        self._get_next_current_state(s_[0], a),
                        self._get_next_current_state(s_[1], a)
                    })
                    if s2 in table and table[s2]:
                        table[s] = True
                        changed = True
                        break

    def _join_non_marked_states(self, table):
        """Join all overlapping non-marked pairs of states to a new state."""
        non_marked_states = set(filter(lambda s: not table[s], table.keys()))
        changed = True
        while changed:
            changed = False
            for s, s2 in itertools.combinations(non_marked_states, 2):
                if s2.isdisjoint(s):
                    continue
                # merge them!
                s3 = s.union(s2)
                # remove the old ones
                non_marked_states.remove(s)
                non_marked_states.remove(s2)
                # add the new one
                non_marked_states.add(s3)
                # set the changed flag
                changed = True
                break
        # finally adjust the DFA
        for s in non_marked_states:
            stringified = DFA._stringify_states(s)
            # add the new state
            self.states.add(stringified)
            # copy the transitions from one of the states
            self.transitions[stringified] = self.transitions[tuple(s)[0]]
            # replace all occurrences of the old states
            for state in s:
                self.states.remove(state)
                del self.transitions[state]
                for src_state, transition in self.transitions.items():
                    for symbol in transition.keys():
                        if transition[symbol] == state:
                            transition[symbol] = stringified
                if state in self.final_states:
                    self.final_states.add(stringified)
                    self.final_states.remove(state)
                if state == self.initial_state:
                    self.initial_state = stringified

    @staticmethod
    def _stringify_states(states):
        """Stringify the given set of states as a single state name."""
        if isinstance(states, (set, frozenset)):
            states = sorted(states)
        return '{{{}}}'.format(','.join(states))

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
            state_queue.put(next_current_states)

    @classmethod
    def from_nfa(cls, nfa):
        """Initialize this DFA as one equivalent to the given NFA."""
        dfa_states = set()
        dfa_symbols = nfa.input_symbols
        dfa_transitions = {}
        dfa_initial_state = cls._stringify_states((nfa.initial_state,))
        dfa_final_states = set()

        state_queue = queue.Queue()
        state_queue.put({nfa.initial_state})
        while not state_queue.empty():

            current_states = state_queue.get()
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
