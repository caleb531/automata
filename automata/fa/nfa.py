#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic finite automata."""
from __future__ import annotations

import string
from collections import deque
from itertools import chain, count, product, repeat
from typing import (
    AbstractSet,
    Any,
    Deque,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
)

import networkx as nx
from cached_method import cached_method
from frozendict import frozendict
from typing_extensions import Self

import automata.base.exceptions as exceptions
import automata.fa.dfa as dfa
import automata.fa.fa as fa
from automata.regex.parser import RESERVED_CHARACTERS, parse_regex

NFAStateT = fa.FAStateT

NFAPathT = Mapping[str, AbstractSet[NFAStateT]]
NFATransitionsT = Mapping[NFAStateT, NFAPathT]
InputPathListT = List[Tuple[NFAStateT, NFAStateT, str]]
DEFAULT_REGEX_SYMBOLS = frozenset(chain(string.ascii_letters, string.digits))


class NFA(fa.FA):
    """A nondeterministic finite automaton."""

    __slots__: Tuple[str, ...] = (
        "states",
        "input_symbols",
        "transitions",
        "initial_state",
        "final_states",
        # These two entries are to allow for caching methods
        "__dict__",
        "__weakref__",
    )

    transitions: NFATransitionsT

    def __init__(
        self,
        *,
        states: AbstractSet[NFAStateT],
        input_symbols: AbstractSet[str],
        transitions: NFATransitionsT,
        initial_state: NFAStateT,
        final_states: AbstractSet[NFAStateT],
    ) -> None:
        """Initialize a complete NFA."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
        )

    @cached_method
    def _get_lambda_closures(self) -> Mapping[NFAStateT, FrozenSet[NFAStateT]]:
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
        lambda_graph.add_nodes_from(self.states)
        lambda_graph.add_edges_from(
            (
                (start_state, end_state)
                for start_state, transition in self.transitions.items()
                for char, end_states in transition.items()
                if char == ""
                for end_state in end_states
            )
        )

        return frozendict(
            {
                state: frozenset(nx.descendants(lambda_graph, state) | {state})
                for state in self.states
            }
        )

    def __add__(self, other: NFA) -> Self:
        """Return the concatenation of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.concatenate(other)
        else:
            return NotImplemented

    def __or__(self, other: NFA) -> Self:
        """Return the union of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.union(other)
        else:
            return NotImplemented

    def __and__(self, other: NFA) -> Self:
        """Return the union of this NFA and another NFA."""
        if isinstance(other, NFA):
            return self.intersection(other)
        else:
            return NotImplemented

    @classmethod
    def from_dfa(cls: Type[Self], target_dfa: dfa.DFA) -> Self:
        """
        Initialize this NFA as one equivalent to the given DFA.

        Parameters
        ----------
        target_dfa : DFA
            The DFA to construct an equivalent NFA for.

        Returns
        ------
        Self
            The NFA accepting the language of the input DFA.

        """
        nfa_transitions = {
            start_state: {
                input_symbol: {end_state} for input_symbol, end_state in paths.items()
            }
            for start_state, paths in target_dfa.transitions.items()
        }

        return cls(
            states=target_dfa.states,
            input_symbols=target_dfa.input_symbols,
            transitions=nfa_transitions,
            initial_state=target_dfa.initial_state,
            final_states=target_dfa.final_states,
        )

    def _validate_transition_invalid_symbols(
        self, start_state: NFAStateT, paths: NFAPathT
    ) -> None:
        """Raise an error if transition symbols are invalid."""
        for input_symbol in paths.keys():
            if input_symbol not in self.input_symbols and input_symbol != "":
                raise exceptions.InvalidSymbolError(
                    "state {} has invalid transition symbol {}".format(
                        start_state, input_symbol
                    )
                )

    @classmethod
    def from_regex(
        cls: Type[Self], regex: str, *, input_symbols: Optional[AbstractSet[str]] = None
    ) -> Self:
        """
        Initialize this NFA as one equivalent to the given regular expression.

        Parameters
        ----------
        regex : str
            The regex to construct an equivalent NFA for.
        input_symbols : Optional[AbstractSet[str]], default: None
            The set of input symbols to create the NFA over. If not
            set, defaults to all ascii letters and digits.

        Returns
        ------
        Self
            The NFA accepting the language of the input regex.
        """

        if input_symbols is None:
            input_symbols = DEFAULT_REGEX_SYMBOLS
        else:
            conflicting_symbols = RESERVED_CHARACTERS & input_symbols
            if conflicting_symbols:
                raise exceptions.InvalidSymbolError(
                    f"Invalid input symbols: {conflicting_symbols}"
                )

        nfa_builder = parse_regex(regex, input_symbols)

        return cls(
            states=frozenset(nfa_builder._transitions.keys()),
            input_symbols=input_symbols,
            transitions=nfa_builder._transitions,
            initial_state=nfa_builder._initial_state,
            final_states=nfa_builder._final_states,
        )

    def _validate_transition_end_states(
        self, start_state: NFAStateT, paths: NFAPathT
    ) -> None:
        """Raise an error if transition end states are invalid."""
        for end_states in paths.values():
            for end_state in end_states:
                if end_state not in self.states:
                    raise exceptions.InvalidStateError(
                        "end state {} for transition on {} is "
                        "not valid".format(end_state, start_state)
                    )

    def validate(self) -> None:
        """
        Raises an exception if this automaton is not internally consistent.

        Raises
        ------
        InvalidStateError
            If this NFA does has invalid states in the transition dictionary.
        MissingStateError
            If this NFA has states missing from the transition dictionary.
        InvalidSymbolError
            If this NFA has invalid symbols in the transition dictionary.
        """
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
            self._validate_transition_end_states(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_final_states()

    def _iterate_through_symbol_path_pairs(
        self, current_states: AbstractSet[NFAStateT]
    ) -> Generator[Tuple[str, FrozenSet[NFAStateT]], None, None]:
        """
        Iterate through input symbols with set of end transitions which are nonempty.
        """

        lambda_closures = self._get_lambda_closures()
        res_dict: Dict[str, Set[NFAStateT]] = {}

        for input_symbol, next_states in chain.from_iterable(
            self.transitions.get(state, {}).items() for state in current_states
        ):
            # Ignore empty string and empty end states
            if input_symbol and next_states:
                input_symbol_set = res_dict.setdefault(input_symbol, set())
                for end_state in next_states:
                    input_symbol_set.update(lambda_closures[end_state])

        for input_symbol, next_states in res_dict.items():
            yield (input_symbol, frozenset(next_states))

    def _get_next_current_states(
        self, current_states: AbstractSet[NFAStateT], input_symbol: str
    ) -> FrozenSet[NFAStateT]:
        """Return the next set of current states given the current set."""
        next_current_states: Set[NFAStateT] = set()
        lambda_closures = self._get_lambda_closures()

        for current_state in current_states:
            if current_state not in self.transitions:
                continue
            current_transition = self.transitions[current_state]
            for end_state in current_transition.get(input_symbol, {}):
                next_current_states.update(lambda_closures[end_state])

        return frozenset(next_current_states)

    @staticmethod
    def _compute_reachable_states(
        initial_state: NFAStateT, transitions: NFATransitionsT
    ) -> Set[NFAStateT]:
        """Compute the states which are reachable from the initial state."""

        visited_set: Set[NFAStateT] = set()
        queue: Deque[NFAStateT] = deque()

        queue.append(initial_state)
        visited_set.add(initial_state)

        while queue:
            state = queue.popleft()
            state_dict = transitions.get(state)

            if state_dict:
                for next_state in chain.from_iterable(
                    dest for dest in state_dict.values()
                ):
                    if next_state not in visited_set:
                        visited_set.add(next_state)
                        queue.append(next_state)

        return visited_set

    def _eliminate_lambda(
        self,
    ) -> Tuple[AbstractSet[NFAStateT], NFATransitionsT, AbstractSet[NFAStateT]]:
        """Internal helper function for eliminate lambda. Doesn't create final NFA."""

        # Create new transitions and final states for running this algorithm
        new_transitions = {
            state: {symbol: set(dest) for symbol, dest in paths.items()}
            for state, paths in self.transitions.items()
        }
        new_final_states = set(self.final_states)
        lambda_closures = self._get_lambda_closures()

        for state in self.states:
            lambda_enclosure = lambda_closures[state] - {state}
            for input_symbol in self.input_symbols:
                next_current_states = set(
                    self._get_next_current_states(lambda_enclosure, input_symbol)
                )

                # Don't do anything if no new current states
                if next_current_states:
                    state_transition_dict = new_transitions.setdefault(state, {})

                    if input_symbol in state_transition_dict:
                        state_transition_dict[input_symbol].update(next_current_states)
                    else:
                        state_transition_dict[input_symbol] = next_current_states

            if not new_final_states.isdisjoint(lambda_enclosure):
                new_final_states.add(state)

            if state in new_transitions:
                new_transitions[state].pop("", None)

        # Remove unreachable states
        reachable_states = self.__class__._compute_reachable_states(
            self.initial_state, new_transitions
        )
        reachable_final_states = reachable_states & new_final_states

        for state in self.states - reachable_states:
            new_transitions.pop(state, None)

        return reachable_states, new_transitions, reachable_final_states

    def eliminate_lambda(self) -> Self:
        """
        Returns an equivalent NFA with lambda transitions removed.

        Returns
        ------
        Self
            The equivalent NFA with lambda transitions removed.
        """

        (
            reachable_states,
            new_transitions,
            reachable_final_states,
        ) = self._eliminate_lambda()

        return self.__class__(
            states=reachable_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=reachable_final_states,
        )

    def _check_for_input_rejection(
        self, current_states: AbstractSet[NFAStateT]
    ) -> None:
        """Raise an error if the given config indicates rejected input."""
        if current_states.isdisjoint(self.final_states):
            raise exceptions.RejectionException(
                "the NFA stopped on all non-final states ({})".format(
                    ", ".join(str(state) for state in current_states)
                )
            )

    def read_input_stepwise(
        self, input_str: str
    ) -> Generator[AbstractSet[NFAStateT], None, None]:
        """
        Return a generator that yields the configuration of this NFA at each
        step while reading input.

        Parameters
        ----------
        input_str : str
            The input string to read.

        Yields
        ------
        Generator[AbstractSet[NFAStateT], None, None]
            A generator that yields the current configuration (a set of states) of
            the NFA after each step of reading input.

        Raises
        ------
        RejectionException
            Raised if this NFA does not accept the input string.
        """
        current_states = self._get_lambda_closures()[self.initial_state]

        yield current_states
        for input_symbol in input_str:
            current_states = self._get_next_current_states(current_states, input_symbol)
            yield current_states

        self._check_for_input_rejection(current_states)

    @staticmethod
    def _get_state_maps(
        state_set_a: AbstractSet[NFAStateT],
        state_set_b: AbstractSet[NFAStateT],
        *,
        start: int = 0,
    ) -> Tuple[Dict[NFAStateT, int], Dict[NFAStateT, int]]:
        """
        Generate state map dicts from given sets. Useful when the state set has
        to be a union of the state sets of component FAs.
        """

        state_name_counter = count(start)

        state_map_a = dict(zip(state_set_a, state_name_counter))
        state_map_b = dict(zip(state_set_b, state_name_counter))

        return (state_map_a, state_map_b)

    def union(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the union of L1 and L2.

        Parameters
        ----------
        other : NFA
            The NFA we want to take a union with.

        Returns
        ------
        Self
            An NFA accepting the union of the two input NFAs.
        """

        # Starting at 1 because 0 is for the initial state
        (state_map_a, state_map_b) = self.__class__._get_state_maps(
            self.states, other.states, start=1
        )

        new_states = frozenset(chain(state_map_a.values(), state_map_b.values(), [0]))
        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {
            state: {} for state in new_states
        }

        # Connect new initial state to both branch
        new_transitions[0] = {
            "": {state_map_a[self.initial_state], state_map_b[other.initial_state]}
        }

        # Transitions of self
        self.__class__._load_new_transition_dict(
            state_map_a, self.transitions, new_transitions
        )
        # Transitions of other
        self.__class__._load_new_transition_dict(
            state_map_b, other.transitions, new_transitions
        )

        # Final states
        new_final_states = frozenset(
            chain(
                (state_map_a[state] for state in self.final_states),
                (state_map_b[state] for state in other.final_states),
            )
        )

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols | other.input_symbols,
            transitions=new_transitions,
            initial_state=0,
            final_states=new_final_states,
        )

    def concatenate(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the language L1 concatenated with L2.

        Parameters
        ----------
        other : NFA
            The NFA we want to concatenate with.

        Returns
        ------
        Self
            An NFA accepting the language concatenation of the two input NFAs.
        """

        (state_map_a, state_map_b) = self.__class__._get_state_maps(
            self.states, other.states
        )

        new_states = frozenset(chain(state_map_a.values(), state_map_b.values()))
        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {
            state: {} for state in new_states
        }

        # Transitions of self
        self.__class__._load_new_transition_dict(
            state_map_a, self.transitions, new_transitions
        )
        # Transitions of other
        self.__class__._load_new_transition_dict(
            state_map_b, other.transitions, new_transitions
        )

        # Transitions from self to other
        for state in self.final_states:
            new_transitions[state_map_a[state]].setdefault("", set()).add(
                state_map_b[other.initial_state]
            )

        # Final states of other
        new_final_states = frozenset(state_map_b[state] for state in other.final_states)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols | other.input_symbols,
            transitions=new_transitions,
            initial_state=state_map_a[self.initial_state],
            final_states=new_final_states,
        )

    def kleene_star(self) -> Self:
        """
        Given an NFA which accepts the language L, returns
        an NFA which accepts L repeated 0 or more times.

        Returns
        ------
        Self
            An NFA accepting the finite repetition of the input NFA.
        """
        new_states = set(self.states)
        new_initial_state = self.__class__._add_new_state(new_states)

        # Transitions are the same with a few additions.
        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = dict(
            self.transitions
        )
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {"": {self.initial_state}}
        # For each final state in original NFA we add epsilon
        # transition to the old initial state
        for state in self.final_states:
            new_transitions[state] = dict(new_transitions.get(state, {}))
            transition = new_transitions[state]
            transition[""] = set(transition.get("", set()))
            transition[""].add(self.initial_state)

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=self.final_states | {new_initial_state},
        )

    def option(self) -> Self:
        """
        Given an NFA which accepts the language L, returns
        an NFA which accepts L repeated 0 or 1 times.

        Returns
        ------
        Self
            An NFA accepting the optional of the input NFA.
        """
        new_states = set(self.states)
        new_initial_state = self.__class__._add_new_state(new_states)

        # Transitions are the same with a few additions.
        new_transitions = dict(self.transitions)
        # We add epsilon transition from new initial state
        # to old initial state
        new_transitions[new_initial_state] = {"": {self.initial_state}}

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=self.final_states | {new_initial_state},
        )

    def reverse(self) -> Self:
        """
        Given an NFA which accepts the language L,
        returns an NFA which accepts the reverse of L.

        Returns
        ------
        Self
            An NFA accepting the reversal of the input NFA.
        """
        new_states = set(self.states)
        new_initial_state = self.__class__._add_new_state(new_states)

        # Transitions are the same except reversed
        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {
            state: {} for state in new_states
        }

        for state_a, transitions in self.transitions.items():
            for symbol, states in transitions.items():
                for state_b in states:
                    new_transitions[state_b].setdefault(symbol, set()).add(state_a)

        # And we additionally have epsilon transitions from
        # new initial state to each old final state.
        new_transitions[new_initial_state][""] = set(self.final_states)
        new_final_states = {self.initial_state}

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
        )

    def intersection(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the intersection of L1 and L2.

        Parameters
        ----------
        other : NFA
            The NFA we want to take an intersection with.

        Returns
        ------
        Self
            An NFA accepting the intersection of the two input NFAs.
        """

        new_states = set()
        new_input_symbols = self.input_symbols | other.input_symbols
        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {}
        new_initial_state = (self.initial_state, other.initial_state)

        queue: Deque[NFAStateT] = deque()

        queue.append(new_initial_state)
        new_states.add(new_initial_state)

        while queue:
            curr_state = queue.popleft()
            q_a, q_b = curr_state

            # States we will consider adding to the queue
            next_states_iterables: List[Iterable[NFAStateT]] = list()

            # Get transition dict for states in self
            transitions_a = self.transitions.get(q_a, {})
            # Add epsilon transitions for first set of transitions
            epsilon_transitions_a = transitions_a.get("")
            if epsilon_transitions_a is not None:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault("", set()).update(
                    zip(epsilon_transitions_a, repeat(q_b))
                )
                next_states_iterables.append(zip(epsilon_transitions_a, repeat(q_b)))

            # Get transition dict for states in other
            transitions_b = other.transitions.get(q_b, {})
            # Add epsilon transitions for second set of transitions
            epsilon_transitions_b = transitions_b.get("")
            if epsilon_transitions_b is not None:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault("", set()).update(
                    zip(repeat(q_a), epsilon_transitions_b)
                )
                next_states_iterables.append(zip(repeat(q_a), epsilon_transitions_b))

            # Add all transitions moving over same input symbols
            for symbol in new_input_symbols:
                end_states_a = transitions_a.get(symbol)
                end_states_b = transitions_b.get(symbol)

                if end_states_a is not None and end_states_b is not None:
                    state_dict = new_transitions.setdefault(curr_state, {})
                    state_dict.setdefault(symbol, set()).update(
                        product(end_states_a, end_states_b)
                    )
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
            final_states=new_final_states,
        )

    def shuffle_product(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the shuffle of L1 and L2.

        Parameters
        ----------
        other : NFA
            The NFA we want to take a shuffle product with.

        Returns
        ------
        Self
            An NFA accepting the shuffle product of the two input NFAs.
        """
        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state)
        new_states = frozenset(product(self.states, other.states))

        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {}

        for curr_state in new_states:
            state_dict = new_transitions.setdefault(curr_state, {})
            q_a, q_b = curr_state

            transitions_a = self.transitions.get(q_a, {})
            for symbol, end_states in transitions_a.items():
                state_dict.setdefault(symbol, set()).update(
                    zip(end_states, repeat(q_b))
                )

            transitions_b = other.transitions.get(q_b, {})
            for symbol, end_states in transitions_b.items():
                state_dict.setdefault(symbol, set()).update(
                    zip(repeat(q_a), end_states)
                )

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=frozenset(product(self.final_states, other.final_states)),
        )

    def right_quotient(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the right quotient of L1 with respect to L2 (L1 / L2).

        Construction is based off of the one described here:
        https://cs.stackexchange.com/a/102043

        Parameters
        ----------
        other : NFA
            The NFA we want to take a right quotient with.

        Returns
        ------
        Self
            An NFA accepting the right quotient of the two input NFAs.
        """

        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        # First, eliminate lambdas because they cause problems with this algorithm
        (
            self_reachable_states,
            self_new_transitions,
            self_reachable_final_states,
        ) = self._eliminate_lambda()
        (
            other_reachable_states,
            other_new_transitions,
            other_reachable_final_states,
        ) = other._eliminate_lambda()

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state, False)
        new_final_states = frozenset(
            product(self_reachable_final_states, other_reachable_final_states, [True])
        )
        new_states = frozenset(
            chain(
                product(self_reachable_states, [other.initial_state], [False]),
                product(self_reachable_states, other_reachable_states, [True]),
            )
        )

        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {}

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

            new_state_dict[""] = {(state, other.initial_state, True)}

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
                    state_dict.setdefault("", set()).update(
                        product(end_states_a, end_states_b, [True])
                    )

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
        )

    def left_quotient(self, other: NFA) -> Self:
        """
        Given two NFAs, M1 and M2, which accept the languages
        L1 and L2 respectively, returns an NFA which accepts
        the left quotient of L1 with respect to L2 (L2 \\ L1).

        Construction is based off of the one described here:
        https://cs.stackexchange.com/a/102043

        Parameters
        ----------
        other : NFA
            The NFA we want to take a left quotient with.

        Returns
        ------
        Self
            An NFA accepting the left quotient of the two input NFAs.
        """

        if not isinstance(other, NFA):
            raise TypeError(f"other must be an NFA, not {other.__class__.__name__}")

        # First, eliminate lambdas because they cause problems with this algorithm
        (
            self_reachable_states,
            self_new_transitions,
            self_reachable_final_states,
        ) = self._eliminate_lambda()
        (
            other_reachable_states,
            other_new_transitions,
            other_reachable_final_states,
        ) = other._eliminate_lambda()

        new_input_symbols = self.input_symbols | other.input_symbols
        new_initial_state = (self.initial_state, other.initial_state, False)
        new_final_states = frozenset(
            product(self_reachable_final_states, other_reachable_final_states, [True])
        )
        new_states = frozenset(
            chain(
                product(self_reachable_states, other_reachable_states, [False]),
                product(self_reachable_states, other_reachable_final_states, [True]),
            )
        )

        new_transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {}

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
                    state_dict.setdefault("", set()).update(
                        product(end_states_a, end_states_b, [False])
                    )

            # Add lambda transition from final state, flipping third entry to true
            if q_b in other_reachable_final_states:
                state_dict = new_transitions.setdefault(curr_state, {})
                state_dict.setdefault("", set()).add((q_a, q_b, True))

        # Populate transitions for after reading the prefix
        for state_a, state_b in product(
            self_reachable_states, other_reachable_final_states
        ):
            new_state = (state_a, state_b, True)
            new_state_dict = new_transitions.setdefault(new_state, {})
            old_transitions_dict = self_new_transitions.get(state_a)

            if old_transitions_dict:
                for symbol, end_states in old_transitions_dict.items():
                    new_state_dict[symbol] = set(
                        zip(end_states, repeat(state_b), repeat(True))
                    )

        return self.__class__(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
        )

    @staticmethod
    def _load_new_transition_dict(
        state_map_dict: Mapping[NFAStateT, NFAStateT],
        old_transition_dict: NFATransitionsT,
        new_transition_dict: Dict[NFAStateT, Dict[str, Set[NFAStateT]]],
    ) -> None:
        """
        Load the new_transition_dict with the old transitions corresponding to
        the given state_map_dict.
        """

        for state_a, transitions in old_transition_dict.items():
            for symbol, states in transitions.items():
                new_transition_dict[state_map_dict[state_a]][symbol] = {
                    state_map_dict[state_b] for state_b in states
                }

    def __eq__(self, other: Any) -> bool:
        """
        Return True if two NFAs are equivalent. Uses an optimized version of
        the extended Hopcroft-Karp algorithm (HKe). See
        https://arxiv.org/abs/0907.5058
        """

        NFAStatesPairT = Tuple[FrozenSet[NFAStateT], int]

        # Must be another NFA and have equal alphabets
        if not isinstance(other, NFA) or self.input_symbols != other.input_symbols:
            return NotImplemented

        operand_nfas = (self, other)
        initial_state_a = (self._get_lambda_closures()[self.initial_state], 0)
        initial_state_b = (other._get_lambda_closures()[other.initial_state], 1)

        def is_final_state(states_pair: NFAStatesPairT) -> bool:
            states, operand_index = states_pair
            nfa = operand_nfas[operand_index]
            # If at least one of the current states is a final state, the
            # condition should satisfy
            return any(
                not nfa.final_states.isdisjoint(nfa._get_lambda_closures()[state])
                for state in states
            )

        def transition(states_pair: NFAStatesPairT, symbol: str) -> NFAStatesPairT:
            states, operand_index = states_pair
            return (
                operand_nfas[operand_index]._get_next_current_states(states, symbol),
                operand_index,
            )

        # Get data structures
        state_sets = nx.utils.union_find.UnionFind([initial_state_a, initial_state_b])
        pair_stack: Deque[Tuple[NFAStatesPairT, NFAStatesPairT]] = deque()

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
    def edit_distance(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        reference_str: str,
        max_edit_distance: int,
        *,
        insertion: bool = True,
        deletion: bool = True,
        substitution: bool = True,
    ) -> Self:
        """
        Constructs the Levenshtein NFA for the given reference_str and given
        Levenshtein distance. This NFA recognizes strings within the given
        Levenshtein distance (commonly called edit distance) of the
        reference_str. Parameters control which error types the NFA will
        recognize (insertions, deletions, or substitutions). At least one error
        type must be set.

        If insertion and deletion are False and substitution is True, then this
        is the same as Hamming distance.

        If insertion and deletion are True and substitution is False, then this
        is the same as LCS distance.

        insertion, deletion, and substitution all default to True.

        Code adapted from:
        http://blog.notdot.net/2010/07/Damn-Cool-Algorithms-Levenshtein-Automata

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the NFA over.
        reference_str : str
            The reference string the NFA will use to recognize other close strings.
        max_edit_distance : int
            The maximum edit distance from the reference string this NFA will recognize.
            Must be positive.
        insertion : bool, default: True
            Whether to recognize insertion edits relative to the reference string.
        deletion : bool, default: True
            Whether to recognize deletion edits relative to the reference string.
        substitution : bool, default: True
            Whether to recognize substitution edits relative to the reference string.

        Returns
        ------
        Self
            An NFA accepting all strings within the given edit distance to the reference
            string.

        Raises
        ------
        ValueError
            Raised if the max_edit_distance is negative or all of the error flags are
            set to False (at least one must be True).
        """
        if max_edit_distance < 0:
            raise ValueError("max_edit_distance must be greater than zero")
        if not (insertion or deletion or substitution):
            raise ValueError(
                "At least one of insertion, deletion, or substitution must be enabled."
            )

        states = frozenset(
            product(range(len(reference_str) + 1), range(max_edit_distance + 1))
        )

        transitions: Dict[NFAStateT, Dict[str, Set[NFAStateT]]] = {}
        final_states = set()

        def add_transition(
            start_state_dict: Dict[str, Set[NFAStateT]],
            end_state: NFAStateT,
            symbol: str,
        ) -> None:
            """Add transition between start and end state on symbol"""
            start_state_dict.setdefault(symbol, set()).add(end_state)

        def add_any_transition(
            start_state_dict: Dict[str, Set[NFAStateT]], end_state: NFAStateT
        ) -> None:
            """Add transition on all symbols between start and end state"""
            for symbol in input_symbols:
                add_transition(start_state_dict, end_state, symbol)

        for (i, symbol), e in product(
            enumerate(reference_str), range(max_edit_distance + 1)
        ):
            state_transition_dict = transitions.setdefault((i, e), {})

            # Correct character
            add_transition(state_transition_dict, (i + 1, e), symbol)
            if e < max_edit_distance:
                if insertion:
                    # Insertion
                    add_any_transition(state_transition_dict, (i, e + 1))

                if deletion:
                    # Deletion
                    add_transition(state_transition_dict, (i + 1, e + 1), "")

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
            final_states=final_states,
        )

    def iter_transitions(
        self,
    ) -> Generator[Tuple[NFAStateT, NFAStateT, str], None, None]:
        """
        Iterate over all transitions in the NFA. Each transition is a tuple
        of the form (from_state, to_state, symbol).

        Returns
        ------
        Generator[Tuple[NFAStateT, NFAStateT, str], None, None]
            The desired generator over the NFA transitions.
        """
        return (
            (from_, to_, symbol)
            for from_, lookup in self.transitions.items()
            for symbol, to_lookup in lookup.items()
            for to_ in to_lookup
        )

    def _get_input_path(self, input_str: str) -> Tuple[InputPathListT, bool]:
        """
        Get best input path. A path is better if (with priority):

        1. It is an accepting path (ends in a final state)
        2. It reads more of the input (if the input is not accepted we
            select the path such that we can stay on the nfa the longest)
        3. It has the fewest jumps (uses less lambda symbols)

        Returns a tuple of:
        1. the path taken
        2. whether the path was accepting
        """

        visited = set()
        work_queue: Deque[Tuple[InputPathListT, NFAStateT, str]] = deque(
            [([], self.initial_state, input_str)]
        )

        last_non_accepting_input: InputPathListT = []
        least_input_remaining = len(input_str)

        while work_queue:
            visited_states, curr_state, remaining_input = work_queue.popleft()

            # First final state we hit is the best according to desired criteria
            if curr_state in self.final_states and not remaining_input:
                return visited_states, True

            # Otherwise, update longest non-accepting input
            if len(remaining_input) < least_input_remaining:
                least_input_remaining = len(remaining_input)
                last_non_accepting_input = visited_states

            # First, get next states that result from reading from input
            if remaining_input:
                next_symbol = remaining_input[0]
                rest = remaining_input[1:] if remaining_input else ""

                next_states_from_symbol = self.transitions[curr_state].get(
                    next_symbol, set()
                )

                for next_state in next_states_from_symbol:
                    if (next_state, rest) not in visited:
                        next_visited_states = visited_states.copy()
                        next_visited_states.append(
                            (curr_state, next_state, next_symbol)
                        )
                        visited.add((next_state, rest))
                        work_queue.append((next_visited_states, next_state, rest))

            # Next, get next states resulting from lambda transition
            next_states_from_lambda = self.transitions[curr_state].get("", set())

            for next_state in next_states_from_lambda:
                if (next_state, remaining_input) not in visited:
                    next_visited_states = visited_states.copy()
                    next_visited_states.append((curr_state, next_state, ""))
                    visited.add((next_state, remaining_input))
                    work_queue.append(
                        (next_visited_states, next_state, remaining_input)
                    )

        return last_non_accepting_input, False
