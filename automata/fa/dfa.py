"""Classes and methods for working with deterministic finite automata."""

from __future__ import annotations

import array
from collections import defaultdict, deque
from itertools import chain, count
from random import Random
from typing import (
    AbstractSet,
    Any,
    Callable,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generator,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)

import networkx as nx
from cached_method import cached_method
from typing_extensions import Self, TypeAlias

import automata.base.exceptions as exceptions
import automata.fa.fa as fa
import automata.fa.nfa as nfa
from automata.base.utils import (
    PartitionRefinement,
    _missing_animation_imports,
    get_reachable_nodes,
    get_renaming_function,
    pairwise,
)

if not _missing_animation_imports:
    from automata.fa.animation import _DFAAnimation
DFAStateT = fa.FAStateT

DFASymbolT = str
DFAPathT = Mapping[DFASymbolT, DFAStateT]
DFATransitionsT = Mapping[DFAStateT, DFAPathT]

ExpandStateReturnType = Iterator[Tuple[DFASymbolT, DFAStateT]]
ExpandStateFn = Callable[[DFAStateT], ExpandStateReturnType]
IsFinalStateFn = Callable[[DFAStateT], bool]
TargetStateFn = Callable[[DFAStateT], bool]


class DFA(fa.FA):
    """
    The `DFA` class is a subclass of `FA` and represents a deterministic finite
    automaton.

    Every DFA can be rendered natively inside of a Jupyter notebook
    (automatically calling `show_diagram` without any arguments) if installed
    with the `visual` optional dependency.

    Parameters
    ----------
    states : AbstractSet[DFAStateT]
        Set of the DFA's valid states.
    input_symbols : AbstractSet[str]
        Set of the DFA's valid input symbols, each of which is a singleton
        string
    transitions : Mapping[DFAStateT, Mapping[str, DFAStateT]]
        Dict consisting of the transitions for each state. Each key is a
        state name, and each value is another dict which maps a symbol
        (the key) to a state (the value).
    initial_state : DFAStateT
        The initial state for this DFA.
    final_states : AbstractSet[DFAStateT]
        A set of final states for this DFA
    allow_partial : bool, default: False
        By default, each DFA state must have a transition to
        every input symbol; if this parameter is `True`, you can disable this
        characteristic (such that any DFA state can have fewer transitions than input
        symbols). Note that a DFA must always have every state represented in the
        transition dictionary, even if there are no transitions on input symbols
        leaving a state (dictionary is left empty in that case).
    """

    __slots__ = (
        "states",
        "input_symbols",
        "transitions",
        "initial_state",
        "final_states",
        "allow_partial",
        "_count_cache",
        "_word_cache",
        # These two entries are to allow for caching methods
        "__dict__",
        "__weakref__",
    )

    allow_partial: bool
    _word_cache: List[DefaultDict[DFAStateT, List[str]]]
    _count_cache: List[DefaultDict[DFAStateT, int]]

    def __init__(
        self,
        *,
        states: AbstractSet[DFAStateT],
        input_symbols: AbstractSet[str],
        transitions: DFATransitionsT,
        initial_state: DFAStateT,
        final_states: AbstractSet[DFAStateT],
        allow_partial: bool = False,
    ) -> None:
        """Initialize a complete DFA."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
            allow_partial=allow_partial,
        )

        self.clear_cache()

    def clear_cache(self) -> None:
        """
        Resets the word and count caches.
        Can be called if too much memory is being used.
        """
        object.__setattr__(self, "_word_cache", [])
        object.__setattr__(self, "_count_cache", [])

    def __eq__(self, other: Any) -> bool:
        """
        Return True if two DFAs are equivalent. Uses an optimized version of
        the Hopcroft-Karp algorithm. See https://arxiv.org/abs/0907.5058
        """

        DFAStatePairT = Tuple[DFAStateT, int]

        # Must be another DFA and have equal alphabets
        if not isinstance(other, DFA) or self.input_symbols != other.input_symbols:
            return NotImplemented

        operand_dfas = (self, other)
        initial_state_a = (self.initial_state, 0)
        initial_state_b = (other.initial_state, 1)

        def is_final_state(state_pair: DFAStatePairT) -> bool:
            state, operand_index = state_pair
            return state in operand_dfas[operand_index].final_states

        def transition(state_pair: DFAStatePairT, symbol: str) -> DFAStatePairT:
            state, operand_index = state_pair
            return (
                operand_dfas[operand_index]._get_next_current_state(state, symbol),
                operand_index,
            )

        # Get data structures
        state_sets = nx.utils.union_find.UnionFind((initial_state_a, initial_state_b))
        pair_stack: Deque[Tuple[DFAStatePairT, DFAStatePairT]] = deque()

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

    def __le__(self, other: DFA) -> bool:
        """Return True if this DFA is a subset of (or equal to) another DFA."""
        if isinstance(other, DFA):
            return self.issubset(other)
        else:
            return NotImplemented

    def __ge__(self, other: DFA) -> bool:
        """Return True if this DFA is a superset of another DFA."""
        if isinstance(other, DFA):
            return self.issuperset(other)
        else:
            return NotImplemented

    def __lt__(self, other: DFA) -> bool:
        """Return True if this DFA is a strict subset of another DFA."""
        if isinstance(other, DFA):
            return self <= other and self != other
        else:
            return NotImplemented

    def __gt__(self, other: DFA) -> bool:
        """Return True if this DFA is a strict superset of another DFA."""
        if isinstance(other, DFA):
            return self >= other and self != other
        else:
            return NotImplemented

    def __sub__(self, other: DFA) -> Self:
        """Return a DFA that is the difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.difference(other)
        else:
            return NotImplemented

    def __or__(self, other: DFA) -> Self:
        """Return the union of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.union(other)
        else:
            return NotImplemented

    def __and__(self, other: DFA) -> Self:
        """Return the intersection of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.intersection(other)
        else:
            return NotImplemented

    def __xor__(self, other: DFA) -> Self:
        """Return the symmetric difference of this DFA and another DFA."""
        if isinstance(other, DFA):
            return self.symmetric_difference(other)
        else:
            return NotImplemented

    def __invert__(self) -> Self:
        """Return the complement of this DFA and another DFA."""
        return self.complement()

    def __iter__(self) -> Iterator[str]:
        """
        Iterates through all words in the language represented by the DFA. The
        words are ordered first by length and then by the order of the input
        symbol set.
        """
        i = self.minimum_word_length()
        limit = self.maximum_word_length()
        while limit is None or i <= limit:
            yield from self.words_of_length(i)
            i += 1

    def __len__(self) -> int:
        """Returns the cardinality of the language represented by the DFA."""
        return self.cardinality()

    def to_partial(self, *, retain_names: bool = False, minify: bool = True) -> Self:
        """
        Turns a DFA (complete or not) into a partial DFA.
        Removes dead states and trap states (except the initial state)
            and all edges leading to them.

        Parameters
        ----------
        minify : bool, default: True
            Whether to perform a minify operation while converting to
            a partial DFA.
        retain_names : bool, default: True
            Whether to retain state names during minification.

        Returns
        -------
        Self
            An equivalent partial DFA.
        """

        # Still want to try and remove dead states in the case of a partial DFA
        graph = self._get_digraph()
        live_states = get_reachable_nodes(graph, [self.initial_state])
        non_trap_states = get_reachable_nodes(graph, self.final_states, reversed=True)

        new_states = live_states & non_trap_states
        new_states.add(self.initial_state)

        if minify:
            # No need to alter transitions here, since unused entries in
            # that dict are removed automatically by the minify call
            return self.__class__._minify(
                reachable_states=new_states,
                input_symbols=self.input_symbols,
                transitions=self.transitions,
                initial_state=self.initial_state,
                reachable_final_states=self.final_states & new_states,
                retain_names=retain_names,
            )

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions={
                src_state: {
                    symbol: tgt_state
                    for symbol, tgt_state in lookup.items()
                    if tgt_state in non_trap_states
                }
                for src_state, lookup in self.transitions.items()
                if src_state in new_states
            },
            initial_state=self.initial_state,
            final_states=self.final_states & new_states,
            allow_partial=True,
        )

    def _get_trap_state_id(self) -> DFAStateT:
        return next(x for x in count(-1, -1) if x not in self.states)

    def to_complete(self, trap_state: Optional[DFAStateT] = None) -> Self:
        """
        Creates an equivalent complete DFA with trap_state used as the name
        for an added trap state. If trap_state is not passed in, defaults to
        the largest negative integer which is not already a state name.
        If the DFA is already complete, just returns a copy.

        Parameters
        ----------
        trap_state : Optional[DFAStateT], default: None
            Name for custom trap state to be used.

        Returns
        -------
        Self
            An equivalent complete DFA.

        """
        is_partial = any(
            len(lookup) != len(self.input_symbols)
            for lookup in self.transitions.values()
        )

        if not is_partial:
            return self.copy()

        if trap_state is None:
            trap_state = self._get_trap_state_id()
        elif trap_state in self.states:
            raise exceptions.InvalidStateError(
                f"state {trap_state} is already in the state set and "
                "cannot be used as a label for the trap state."
            )

        return self._to_complete(
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.final_states,
            trap_state=trap_state,
        )

    @classmethod
    def _to_complete(
        cls: Type[Self],
        *,
        input_symbols: AbstractSet[str],
        transitions: DFATransitionsT,
        initial_state: DFAStateT,
        final_states: AbstractSet[DFAStateT],
        trap_state: DFAStateT,
    ) -> Self:
        """
        Internal helper function taking in a description of a partial DFA and
        returning a corresponding complete DFA.

        Note: This will not work with the description of a complete DFA,
        so be sure the input describes a partial one.
        """

        default_to_trap = {symbol: trap_state for symbol in input_symbols}
        transitions = {
            state: {**default_to_trap, **lookup}
            for state, lookup in transitions.items()
        }
        transitions[trap_state] = default_to_trap

        return cls(
            states=frozenset(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state,
            final_states=final_states,
            allow_partial=False,
        )

    def _validate_transition_missing_symbols(
        self, start_state: DFAStateT, paths: DFAPathT
    ) -> None:
        """Raise an error if the transition input_symbols are missing."""
        if self.allow_partial:
            return
        for input_symbol in self.input_symbols:
            if input_symbol not in paths:
                raise exceptions.MissingSymbolError(
                    f"state {start_state} is missing transitions "
                    f'for symbol "{input_symbol}"'
                )

    def _validate_transition_invalid_symbols(
        self, start_state: DFAStateT, paths: DFAPathT
    ) -> None:
        """Raise an error if transition input symbols are invalid."""
        for input_symbol in paths.keys():
            if input_symbol not in self.input_symbols:
                raise exceptions.InvalidSymbolError(
                    f"state {start_state} has invalid transition symbol"
                    f' "{input_symbol}"'
                )

    def _validate_transition_start_states(self) -> None:
        """Raise an error if transition start states are missing."""
        for state in self.states:
            if state not in self.transitions:
                raise exceptions.MissingStateError(
                    f"transition start state {state} is missing"
                )

    def _validate_transition_end_states(
        self, start_state: DFAStateT, paths: DFAPathT
    ) -> None:
        """Raise an error if transition end states are invalid."""
        for end_state in paths.values():
            if end_state not in self.states:
                raise exceptions.InvalidStateError(
                    f"end state {end_state} for transition on "
                    f"{start_state} is not valid"
                )

    def _validate_transitions(self, start_state: DFAStateT, paths: DFAPathT) -> None:
        """Raise an error if transitions are missing or invalid."""
        self._validate_transition_missing_symbols(start_state, paths)
        self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_transition_end_states(start_state, paths)

    def validate(self) -> None:
        """
        Raises an exception if this automaton is not internally consistent.

        Raises
        ------
        InvalidStateError
            If this DFA has invalid states in the transition dictionary.
        MissingStateError
            If this DFA has states missing from the transition dictionary.
        InvalidSymbolError
            If this DFA has invalid symbols in the transition dictionary.
        MissingSymbolError
            If this DFA is missing transitions on certain symbols.
        """

        self._validate_transition_start_states()
        for start_state, paths in self.transitions.items():
            self._validate_transitions(start_state, paths)
        self._validate_initial_state()
        self._validate_final_states()

    def _get_next_current_state(
        self, current_state: DFAStateT, input_symbol: str
    ) -> Optional[DFAStateT]:
        """
        Follow the transition for the given input symbol on the current state.

        Return None if transition does not exist.
        """
        if (
            current_state is not None
            and input_symbol in self.transitions[current_state]
        ):
            return self.transitions[current_state][input_symbol]
        return None

    def _check_for_input_rejection(self, current_state: DFAStateT) -> None:
        """Raise an error if the given config indicates rejected input."""
        if current_state not in self.final_states:
            raise exceptions.RejectionException(
                f"the DFA stopped on a non-final state ({current_state})"
            )

    def read_input_stepwise(
        self, input_str: str, ignore_rejection: bool = False
    ) -> Generator[DFAStateT, None, None]:
        """
        Return a generator that yields each step while reading input.

        Parameters
        ----------
        input_str : str
            The input string to read.
        ignore_rejection : bool, default: False
            Whether to throw an exception if the input string is rejected.

        Yields
        ------
        Generator[DFAStateT, None, None]
            A generator that yields the current configuration of the DFA
            after each step of reading input.

        Raises
        ------
        RejectionException
            Raised if this DFA does not accept the input string.
        """
        current_state = self.initial_state

        yield current_state
        for input_symbol in input_str:
            current_state = self._get_next_current_state(current_state, input_symbol)
            yield current_state

        if not ignore_rejection:
            self._check_for_input_rejection(current_state)

    def animate_reading_input(self, input_str: str, preview: bool = False) -> None:
        """
        Render the animation of the DFA reading the input string stepwise and save the
        animation in the media/ folder.

        Parameters
        ----------
        input_str : str
            The input string to read.
        preview : bool, default: False
            If true, opens scene in a file viewer.
        """
        if _missing_animation_imports:
            raise _missing_animation_imports
        _DFAAnimation(self, input_str).render(preview)

    @cached_method
    def _get_digraph(self) -> nx.DiGraph:
        """Return a digraph corresponding to this DFA with transition symbols ignored"""

        graph = nx.DiGraph()
        graph.add_nodes_from(self.states)
        graph.add_edges_from(
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for end_state in transition.values()
        )

        return graph

    def minify(self, retain_names: bool = False) -> Self:
        """
        Create a minimal DFA which accepts the same inputs as this DFA.

        First, non-reachable states are removed.
        Then, indistinguishable states are merged using Hopcroft's Algorithm.

        Parameters
        ----------
        retain_names : bool, default: False
            Whether to retain original names when merging states.
            New names are from 0 to n-1.

        Returns
        ------
        Self
            A state-minimal equivalent DFA. May be complete in some cases
            if the input is partial.
        """

        if self.allow_partial:
            # In the case of a partial DFA, we want to try to condense
            # possible trap states before the main minify operation.
            graph = self._get_digraph()
            live_states = get_reachable_nodes(graph, [self.initial_state])
            non_trap_states = get_reachable_nodes(
                graph, self.final_states, reversed=True
            )

            reachable_states = live_states & non_trap_states
            reachable_states.add(self.initial_state)
        else:
            # Compute reachable states and final states
            bfs_states = self.__class__._bfs_states(
                self.initial_state, lambda state: iter(self.transitions[state].items())
            )
            reachable_states = set(bfs_states)

        reachable_final_states = self.final_states & reachable_states

        return self.__class__._minify(
            reachable_states=reachable_states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            reachable_final_states=reachable_final_states,
            retain_names=retain_names,
        )

    @classmethod
    def _minify(
        cls: Type[Self],
        *,
        reachable_states: AbstractSet[DFAStateT],
        input_symbols: AbstractSet[str],
        transitions: DFATransitionsT,
        initial_state: DFAStateT,
        reachable_final_states: AbstractSet[DFAStateT],
        retain_names: bool,
    ) -> Self:
        """
        Minify helper function. DFA data passed in must have no unreachable states.
        If the input DFA is partial, then the result is also a partial DFA
        """

        reachable_states = set(reachable_states)

        # Per input-symbol backmap (tgt -> origin states)
        transition_back_map: Dict[str, Dict[DFAStateT, List[DFAStateT]]] = {
            symbol: {end_state: [] for end_state in reachable_states}
            for symbol in input_symbols
        }

        trap_state = None

        for start_state, path in transitions.items():
            if start_state in reachable_states:
                for symbol in input_symbols:
                    end_state = path.get(symbol)

                    # If statement here needed to ignore certain transitions
                    # for non-reachable states
                    if end_state in reachable_states:
                        symbol_dict = transition_back_map[symbol]
                        symbol_dict[end_state].append(start_state)
                    else:
                        # Add trap state if needed
                        if trap_state is None:
                            trap_state = next(
                                x for x in count(-1, -1) if x not in reachable_states
                            )
                            for trap_symbol in input_symbols:
                                transition_back_map[trap_symbol][trap_state] = [
                                    trap_state
                                ]

                            reachable_states.add(trap_state)

                        transition_back_map[symbol][trap_state].append(start_state)

        # Set up equivalence class data structure
        eq_classes = PartitionRefinement(reachable_states)
        refinement = eq_classes.refine(reachable_final_states)

        final_states_id = (
            refinement[0][0] if refinement else next(iter(eq_classes.get_set_ids()))
        )

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
                new_eq_class_pairs = eq_classes.refine(
                    states_that_move_into_active_state
                )

                for YintX_id, YdiffX_id in new_eq_class_pairs:
                    # Only adding one id to processing, since the other is already there
                    if YdiffX_id in processing:
                        processing.add(YintX_id)
                    else:
                        if len(eq_classes.get_set_by_id(YintX_id)) <= len(
                            eq_classes.get_set_by_id(YdiffX_id)
                        ):
                            processing.add(YintX_id)
                        else:
                            processing.add(YdiffX_id)

        # now eq_classes are good to go, make them a list for ordering
        eq_class_name_pairs: List[Tuple[DFAStateT, Set[DFAStateT]]] = (
            [(frozenset(eq), eq) for eq in eq_classes.get_sets()]
            if retain_names
            else list(enumerate(eq_classes.get_sets()))
        )

        # need a backmap to prevent constant calls to index
        back_map = {
            state: name
            for name, eq in eq_class_name_pairs
            for state in eq
            if trap_state not in eq
        }

        # If only one equivalence class with the trap state,
        # return empty language.
        if not back_map:
            return cls.empty_language(input_symbols)

        new_input_symbols = input_symbols
        new_states = frozenset(back_map.values())
        new_initial_state = back_map[initial_state]
        new_final_states = frozenset(back_map[acc] for acc in reachable_final_states)
        new_transitions = {}

        for name, eq in eq_class_name_pairs:
            # For trap state, can just leave out
            if trap_state in eq:
                continue

            eq_class_rep = next(iter(eq))

            inner_transition_dict_old = transitions[eq_class_rep]
            new_transitions[name] = {
                letter: back_map[inner_transition_dict_old[letter]]
                for letter in inner_transition_dict_old.keys()
                if inner_transition_dict_old[letter] in back_map.keys()
            }

        allow_partial = any(
            len(lookup) != len(input_symbols) for lookup in new_transitions.values()
        )
        return cls(
            states=new_states,
            input_symbols=new_input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=new_final_states,
            allow_partial=allow_partial,
        )

    def union(
        self, other: DFA, *, retain_names: bool = False, minify: bool = True
    ) -> Self:
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the union of L1 and L2.

        Minifies by default. Unreachable states are always removed.
        If either input DFA is partial, the result is partial.

        Parameters
        ----------
        other : DFA
            The DFA we want to take a union with.
        retain_names : bool, default: False
            Whether to retain state names through the union and optional minify.
        minify : bool, default: True
            Whether to minify the result of the union of the two DFAs.

        Returns
        ------
        Self
            A DFA accepting the union of the two input DFAs. State minimal by
            default.
        """

        def union_function(state_pair: Tuple[DFAStateT, DFAStateT]) -> bool:
            q_a, q_b = state_pair
            return q_a in self.final_states or q_b in other.final_states

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=True, rhs_relevant=True
        )

        return self.__class__._expand_dfa(
            union_function,
            initial_state,
            expand_state_fn,
            self.input_symbols,
            retain_names=retain_names,
            minify=minify,
        )

    def intersection(
        self, other: DFA, *, retain_names: bool = False, minify: bool = True
    ) -> Self:
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the intersection of L1 and L2.

        Minifies by default. Unreachable states are always removed.
        If either input DFA is partial, the result is partial.

        Parameters
        ----------
        other : DFA
            The DFA we want to take a intersection with.
        retain_names : bool, default: False
            Whether to retain state names through the intersection and optional minify.
        minify : bool, default: True
            Whether to minify the result of the intersection of the two DFAs.

        Returns
        ------
        Self
            A DFA accepting the intersection of the two input DFAs. State minimal by
            default.
        """

        def intersection_function(state_pair: Tuple[DFAStateT, DFAStateT]) -> bool:
            q_a, q_b = state_pair
            return q_a in self.final_states and q_b in other.final_states

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=False, rhs_relevant=False
        )

        return self.__class__._expand_dfa(
            intersection_function,
            initial_state,
            expand_state_fn,
            self.input_symbols,
            retain_names=retain_names,
            minify=minify,
        )

    def difference(
        self, other: DFA, *, retain_names: bool = False, minify: bool = True
    ) -> Self:
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the difference of L1 and L2.

        Minifies by default. Unreachable states are always removed.
        If either input DFA is partial, the result is partial.

        Parameters
        ----------
        other : DFA
            The DFA we want to take a difference with.
        retain_names : bool, default: False
            Whether to retain state names through the difference and optional minify.
        minify : bool, default: True
            Whether to minify the result of the difference of the two DFAs.

        Returns
        ------
        Self
            A DFA accepting the difference of the two input DFAs. State minimal by
            default.
        """

        def difference_function(state_pair: Tuple[DFAStateT, DFAStateT]) -> bool:
            q_a, q_b = state_pair
            return q_a in self.final_states and q_b not in other.final_states

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=False, rhs_relevant=True
        )

        return self.__class__._expand_dfa(
            difference_function,
            initial_state,
            expand_state_fn,
            self.input_symbols,
            retain_names=retain_names,
            minify=minify,
        )

    def symmetric_difference(
        self, other: DFA, *, retain_names: bool = False, minify: bool = True
    ) -> Self:
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the symmetric difference of L1 and L2.

        Minifies by default. Unreachable states are always removed.
        If either input DFA is partial, the result is partial.

        Parameters
        ----------
        other : DFA
            The DFA we want to take a symmetric difference with.
        retain_names : bool, default: False
            Whether to retain state names through the symmetric difference and optional
            minify.
        minify : bool, default: True
            Whether to minify the result of the symmetric difference of the two DFAs.

        Returns
        ------
        Self
            A DFA accepting the symmetric difference of the two input DFAs. State
            minimal by default.
        """

        def symmetric_difference_function(
            state_pair: Tuple[DFAStateT, DFAStateT],
        ) -> bool:
            q_a, q_b = state_pair
            return (q_a in self.final_states) ^ (q_b in other.final_states)

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=True, rhs_relevant=True
        )

        return self.__class__._expand_dfa(
            symmetric_difference_function,
            initial_state,
            expand_state_fn,
            self.input_symbols,
            retain_names=retain_names,
            minify=minify,
        )

    def complement(self, *, retain_names: bool = False, minify: bool = True) -> Self:
        """
        Creates a DFA which accepts an input if and only if the old one does not.
        Minifies by default. Unreachable states are always removed. Partial DFAs
        are converted into complete ones.

        Parameters
        ----------
        retain_names : bool, default: False
            Whether to retain state names through the complement and optional
            minify.
        minify : bool, default: True
            Whether to minify the result of the complement of the input DFA.

        Returns
        ------
        Self
            A DFA accepting the complement of the input DFA. State
            minimal by default.
        """

        # We can't do much here, we must turn it into a complete DFA
        complete_dfa: Self = self.to_complete() if self.allow_partial else self

        if minify:
            bfs_states = self.__class__._bfs_states(
                complete_dfa.initial_state,
                lambda state: iter(complete_dfa.transitions[state].items()),
            )

            reachable_states = set(bfs_states)
            reachable_final_states = complete_dfa.final_states & reachable_states

            return complete_dfa.__class__._minify(
                reachable_states=reachable_states,
                input_symbols=complete_dfa.input_symbols,
                transitions=complete_dfa.transitions,
                initial_state=complete_dfa.initial_state,
                reachable_final_states=reachable_states - reachable_final_states,
                retain_names=retain_names,
            )

        return complete_dfa.__class__(
            states=complete_dfa.states,
            input_symbols=complete_dfa.input_symbols,
            transitions=complete_dfa.transitions,
            initial_state=complete_dfa.initial_state,
            final_states=complete_dfa.states - complete_dfa.final_states,
        )

    @staticmethod
    def _bfs_edges(
        initial_state: DFAStateT,
        expand_state_fn: ExpandStateFn,
    ) -> Generator[Tuple[DFAStateT, DFASymbolT, DFAStateT], None, None]:
        """
        Emits the edges (src_state, label, tgt_state) visited by BFS from the
        initial_state. Computes subsequent states using the function expand_state_fn.
        """
        visited_set = {initial_state}
        queue: Deque[Tuple[DFAStateT, DFAStateT]] = deque([initial_state])

        while queue:
            curr_state = queue.popleft()

            for chr, tgt_state in expand_state_fn(curr_state):
                yield curr_state, chr, tgt_state

                if tgt_state not in visited_set:
                    visited_set.add(tgt_state)
                    queue.append(tgt_state)

    @staticmethod
    def _bfs_states(
        initial_state: DFAStateT, expand_state_fn: ExpandStateFn
    ) -> Generator[DFAStateT, None, None]:
        """
        Emits the states visited by BFS from the initial_state.
        Computes subsequent states using the function expand_state_fn.
        """
        yield initial_state
        visited_set = {initial_state}
        queue = deque([initial_state])

        while queue:
            curr_state = queue.popleft()

            for _, tgt_state in expand_state_fn(curr_state):
                if tgt_state not in visited_set:
                    yield tgt_state
                    visited_set.add(tgt_state)
                    queue.append(tgt_state)

    @classmethod
    def _expand_dfa(
        cls: Type[Self],
        final_state_fn: IsFinalStateFn,
        initial_state: DFAStateT,
        expand_state_fn: ExpandStateFn,
        input_symbols: AbstractSet[DFASymbolT],
        retain_names: bool = False,
        minify: bool = True,
    ) -> Self:
        """
        Constructs the DFA by expanding from the initial_state using the expand_state_fn
        function. The function final_state_fn must return True for the final states.
        The function expand_state_fn must return an iterator with the successors
        of each state in the product.

        If minify is set to True, the returned DFA is minified. If retain_names
        is set to False, states are renamed.
        """

        if retain_names:

            def get_name_original(state: DFAStateT) -> DFAStateT:
                return state

            get_name: Callable[[DFAStateT], DFAStateT] = get_name_original
        else:
            get_name = get_renaming_function(count(0))

        initial_state_name = get_name(initial_state)

        transitions: Dict[DFAStateT, Dict[str, DFAStateT]] = {initial_state_name: {}}
        states = {initial_state_name}
        final_states = {initial_state_name} if final_state_fn(initial_state) else set()

        for cur_state, chr, tgt_state in cls._bfs_edges(initial_state, expand_state_fn):
            cur_state_name = get_name(cur_state)
            tgt_state_name = get_name(tgt_state)

            if tgt_state_name not in states:
                states.add(tgt_state_name)
                transitions[tgt_state_name] = {}

            transitions[cur_state_name][chr] = tgt_state_name

            if final_state_fn(tgt_state):
                final_states.add(tgt_state_name)

        if minify:
            # From the construction, the states/final states are reachable
            return cls._minify(
                reachable_states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state_name,
                reachable_final_states=final_states,
                retain_names=retain_names,
            )

        # This method is generic and is used to implement (mostly) binary
        #   operators; we don't offer the option to return complete/partial
        #   DFAs; instead this is inferred directly from the structure of the
        #   resulting DFA. But for these operations, the result will be a
        #   complete DFA if the inputs are also complete DFAs
        is_partial = any(
            len(lookup) != len(input_symbols) for lookup in transitions.values()
        )
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=initial_state_name,
            final_states=final_states,
            allow_partial=is_partial,
        )

    @classmethod
    def _find_state(
        cls: Type[Self],
        target_state_fn: TargetStateFn,
        initial_state: DFAStateT,
        expand_state_fn: ExpandStateFn,
    ) -> bool:
        """
        Searches for a target state in the DFA without explicitly constructing
        it. The function target_state_fn should return True for states that are being
        searched for. The expand_state_fn should return an iterator with the
        successors of each state in the product.
        """
        bfs_states = cls._bfs_states(initial_state, expand_state_fn)
        return any(target_state_fn(state) for state in bfs_states)

    @staticmethod
    def _cross_product(
        lhs: DFA, rhs: DFA, *, lhs_relevant: bool, rhs_relevant: bool
    ) -> Tuple[DFAStateT, ExpandStateFn]:
        """
        Builds the cross product between the two DFAs.
        Keeps expanding the lhs and rhs if the trap state is encountered based on the
        lhs_relevant and rhs_relevant booleans.
        """

        if lhs.input_symbols != rhs.input_symbols:
            raise exceptions.SymbolMismatchError(
                "The input symbols between the two given DFAs do not match"
            )

        trap_a = lhs._get_trap_state_id()
        trap_b = rhs._get_trap_state_id()

        # TODO if anyone ever has issues with this function being too slow,
        # there is a way to speed this up in special cases with some complicated
        # logic with the lhs_relevant and rhs_relevant booleans and the inner
        # chr loop below.

        def expand_state_fn(state: DFAStateT) -> ExpandStateReturnType:
            q_a, q_b = state
            # Have to use .get() here since these might be trap states
            transitions_a = lhs.transitions.get(q_a, {})
            transitions_b = rhs.transitions.get(q_b, {})

            for chr in transitions_a.keys() | transitions_b.keys():
                # Equivalent to reaching the trap state, skip ahead if irrelevant
                if not lhs_relevant and chr not in transitions_a:
                    continue
                elif not rhs_relevant and chr not in transitions_b:
                    continue

                yield (
                    chr,
                    (
                        transitions_a.get(chr, trap_a),
                        transitions_b.get(chr, trap_b),
                    ),
                )

        initial_state = (lhs.initial_state, rhs.initial_state)

        return initial_state, expand_state_fn

    def issubset(self, other: DFA) -> bool:
        """
        Returns True if the language accepted by self is a subset of that of other.

        Parameters
        ----------
        other : DFA
            The other DFA we are comparing our language against.

        Returns
        ------
        bool
            True if self is a subset of other, False otherwise.
        """

        def subset_state_fn(state_pair: Tuple[DFAStateT, DFAStateT]) -> bool:
            """Check for reachable state that is counterexample to subset"""
            q_a, q_b = state_pair
            return q_a in self.final_states and q_b not in other.final_states

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=False, rhs_relevant=True
        )

        return not self.__class__._find_state(
            subset_state_fn, initial_state, expand_state_fn
        )

    def issuperset(self, other: DFA) -> bool:
        """
        Returns True if the language accepted by self is a superset of that of other.

        Parameters
        ----------
        other : DFA
            The other DFA we are comparing our language against.

        Returns
        ------
        bool
            True if self is a superset of other, False otherwise.
        """
        return other.issubset(self)

    def isdisjoint(self, other: DFA) -> bool:
        """
        Returns True if the language accepted by self is disjoint from that of other.

        Parameters
        ----------
        other : DFA
            The other DFA we are comparing our language against.

        Returns
        ------
        bool
            True if self is disjoint from other, False otherwise.
        """

        def disjoint_state_fn(state_pair: Tuple[DFAStateT, DFAStateT]) -> bool:
            """Check for reachable state that is counterexample to disjointness"""
            q_a, q_b = state_pair
            return q_a in self.final_states and q_b in other.final_states

        initial_state, expand_state_fn = self.__class__._cross_product(
            self, other, lhs_relevant=False, rhs_relevant=False
        )

        return not self.__class__._find_state(
            disjoint_state_fn,
            initial_state,
            expand_state_fn,
        )

    @cached_method
    def isempty(self) -> bool:
        """
        Returns True if the language accepted by self is empty.

        Returns
        ------
        bool
            True if self accepts the empty language, False otherwise.
        """
        return not self.__class__._find_state(
            self.final_states.__contains__,
            self.initial_state,
            lambda state: iter(self.transitions[state].items()),
        )

    @cached_method
    def isfinite(self) -> bool:
        """
        Returns True if the language accepted by self is finite.

        Returns
        ------
        bool
            True if self accepts a finite language, False otherwise.
        """
        try:
            return self.maximum_word_length() is not None
        except exceptions.EmptyLanguageException:
            return True

    def random_word(self, k: int, *, seed: Optional[int] = None) -> str:
        """
        Returns a random word of length k accepted by self.

        Parameters
        ----------
        k : int
            The length of the desired word.
        seed : Optional[int], default: None
            The random seed to use for the sampling of the random word.

        Returns
        ------
        str
            A uniformly random word of length k accepted by the DFA self.

        Raises
        ------
        ValueError
            If this DFA does not accept any words of length k.
        """
        self._populate_count_cache_up_to_len(k)
        state = self.initial_state
        if self._count_cache[k][state] == 0:
            raise ValueError(f"Language has no words of length {k}")

        result = []
        rng = Random(seed)
        for remaining in range(k, 0, -1):
            total = self._count_cache[remaining][state]
            choice = rng.randint(0, total - 1)
            transition = self.transitions[state]
            for symbol, next_state in transition.items():
                next_state_count = self._count_cache[remaining - 1][next_state]
                if choice < next_state_count:
                    result.append(symbol)
                    state = next_state
                    break
                choice -= next_state_count

        assert state in self.final_states
        return "".join(result)

    def predecessor(
        self,
        input_str: str,
        *,
        strict: bool = True,
        key: Optional[Callable[[Any], Any]] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> Optional[str]:
        """
        Returns the first string accepted by the DFA that comes before
        the input string in lexicographical order.

        Parameters
        ----------
        input_str : str
            The starting input string.
        strict : bool, default: True
            If set to false and input_str is accepted by the DFA, input_str will be
            returned.
        key : Optional[Callable], default: None
            Function for defining custom lexicographical ordering. Defaults to using
            the standard string ordering.
        min_length : int, default: 0
            Limits generation to words with at least the given length.
        max_length : Optional[int], default: None
            Limits generation to words with at most the given length.

        Returns
        ------
        str
            The first string accepted by the DFA lexicographically before input_string.

        Raises
        ------
        InfiniteLanguageException
            Raised if the language accepted by self is infinite, as we cannot
            generate predecessors in this case.
        """
        for word in self.predecessors(
            input_str,
            strict=strict,
            key=key,
            min_length=min_length,
            max_length=max_length,
        ):
            return word
        return None

    def predecessors(
        self,
        input_str: str,
        *,
        strict: bool = True,
        key: Optional[Callable[[Any], Any]] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """
        Generates all strings that come before the input string
        in lexicographical order.

        Parameters
        ----------
        input_str : str
            The starting input string.
        strict : bool, default: True
            If set to false and input_str is accepted by the DFA, input_str will be
            returned.
        key : Optional[Callable], default: None
            Function for defining custom lexicographical ordering. Defaults to using
            the standard string ordering.
        min_length : int, default: 0
            Limits generation to words with at least the given length.
        max_length : Optional[int], default: None
            Limits generation to words with at most the given length.

        Returns
        ------
        Generator[str, None, None]
            A generator for all strings that come before the input string in
            lexicographical order.

        Raises
        ------
        InfiniteLanguageException
            Raised if the language accepted by self is infinite, as we cannot
            generate predecessors in this case.
        """
        yield from self.successors(
            input_str,
            strict=strict,
            reverse=True,
            key=key,
            min_length=min_length,
            max_length=max_length,
        )

    def successor(
        self,
        input_str: Optional[str],
        *,
        strict: bool = True,
        key: Optional[Callable[[Any], Any]] = None,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> Optional[str]:
        """
        Returns the first string accepted by the DFA that comes after
        the input string in lexicographical order.

        Parameters
        ----------
        input_str : Optional[str]
            The starting input string. If None, will generate all words.
        strict : bool, default: True
            If set to false and input_str is accepted by the DFA, input_str will be
            returned.
        key : Optional[Callable], default: None
            Function for defining custom lexicographical ordering. Defaults to using
            the standard string ordering.
        min_length : int, default: 0
            Limits generation to words with at least the given length.
        max_length : Optional[int], default: None
            Limits generation to words with at most the given length.

        Returns
        ------
        str
            The first string accepted by the DFA lexicographically before input_string.
        """
        for word in self.successors(
            input_str,
            strict=strict,
            key=key,
            min_length=min_length,
            max_length=max_length,
        ):
            return word
        return None

    def successors(
        self,
        input_str: Optional[str],
        *,
        strict: bool = True,
        key: Optional[Callable[[Any], Any]] = None,
        reverse: bool = False,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """
        Generates all strings that come after the input string
        in lexicographical order.

        Parameters
        ----------
        input_str : Optional[str]
            The starting input string. If None, will generate all words.
        strict : bool, default: True
            If set to false and input_str is accepted by the DFA, input_str will be
            returned.
        key : Optional[Callable], default: None
            Function for defining custom lexicographical ordering. Defaults to using
            the standard string ordering.
        reverse : bool, default: False
            If True, then predecessors will be generated instead of successors.
        min_length : int, default: 0
            Limits generation to words with at least the given length.
        max_length : Optional[int], default: None
            Limits generation to words with at most the given length.

        Returns
        ------
        Generator[str, None, None]
            A generator for all strings that come after the input string in
            lexicographical order.

        """
        # A predecessor for a finite string may be infinite but a successor for
        # a finite string is always finite
        if reverse and not self.isfinite():
            raise exceptions.InfiniteLanguageException(
                "Predecessors cannot be computed for infinite languages"
            )
        graph = self._get_digraph()
        coaccessible_nodes = get_reachable_nodes(
            graph, self.final_states, reversed=True
        )

        # Precomputations and setup
        include_input = not strict
        sorted_symbols = sorted(self.input_symbols, reverse=reverse, key=key)
        symbol_succ: Dict[str, Optional[str]] = {
            symbol_a: symbol_b for symbol_a, symbol_b in pairwise(sorted_symbols)
        }
        symbol_succ[sorted_symbols[-1]] = None
        # Special case for None
        state_stack: Deque[Optional[DFAStateT]] = deque(
            [self.initial_state]
            if input_str is None
            else self.read_input_stepwise(input_str, ignore_rejection=True)
        )
        char_stack: Deque[str] = deque("" if input_str is None else input_str)
        first_symbol = sorted_symbols[0]
        # For predecessors we need to special case the input string None
        candidate = None if reverse and input_str is not None else first_symbol
        # If input_str is None then we yield on first value found no matter the
        # value of include_input
        should_yield = include_input or input_str is None

        # Iterative preorder/postorder (depends on reverse) traversal that
        # yields on final states
        while char_stack or candidate is not None:
            state = state_stack[-1]
            # Successors yield here
            if (
                not reverse
                and should_yield
                and min_length <= len(char_stack)
                and (max_length is None or len(char_stack) <= max_length)
                and candidate == first_symbol
                and state in self.final_states
            ):
                yield "".join(char_stack)
            candidate_state = (
                None
                if candidate is None
                else self._get_next_current_state(state, candidate)
            )
            # Traverse to child if candidate is viable
            if candidate_state in coaccessible_nodes and (
                max_length is None or len(char_stack) < max_length
            ):
                state_stack.append(candidate_state)
                char_stack.append(cast(str, candidate))
                candidate = first_symbol
            else:
                # Predecessors yield here
                if (
                    reverse
                    and should_yield
                    and min_length <= len(char_stack)
                    and (max_length is None or len(char_stack) <= max_length)
                    and candidate is None
                    and state in self.final_states
                ):
                    yield "".join(char_stack)
                # Candidate is None means no more children to explore, so
                # traverse to parent
                if candidate is None:
                    state = state_stack.pop()
                    candidate = char_stack.pop()
                candidate = symbol_succ[candidate]
            should_yield = True
        # Predecessor yields here for empty string
        if (
            reverse
            and should_yield
            and min_length <= len(char_stack)
            and (max_length is None or len(char_stack) <= max_length)
            and candidate is None
            and state in self.final_states
        ):
            yield "".join(char_stack)

    def count_words_of_length(self, k: int) -> int:
        """
        Returns count of words of length k accepted by the DFA.

        Parameters
        ----------
        k : int
            The desired word length.

        Returns
        ------
        int
            The number of words of length k accepted by self.
        """
        self._populate_count_cache_up_to_len(k)
        return self._count_cache[k][self.initial_state]

    def _populate_count_cache_up_to_len(self, k: int) -> None:
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
                prev_level = self._count_cache[i - 1]
                level.update(
                    {
                        state: sum(
                            prev_level[suffix_state]
                            for suffix_state in self.transitions[state].values()
                        )
                        for state in self.states
                    }
                )

    def words_of_length(self, k: int) -> Generator[str, None, None]:
        """
        Generates all words of length `k` in the language accepted by the DFA.

        Parameters
        ----------
        k : int
            The desired word length.

        Returns
        ------
        Generator[str, None, None]
            A generator for all words of length k accepted by the DFA.
        """
        self._populate_word_cache_up_to_len(k)
        for word in self._word_cache[k][self.initial_state]:
            yield word

    def _populate_word_cache_up_to_len(self, k: int) -> None:
        """
        Populate word cache up to length k
        """

        # Weird construction to account for partial DFAs.
        sorted_transition_symbols = {
            state: sorted(lookup.keys()) for state, lookup in self.transitions.items()
        }

        while len(self._word_cache) <= k:
            i = len(self._word_cache)
            self._word_cache.append(defaultdict(list))
            level = self._word_cache[i]
            if i == 0:
                level.update({state: [""] for state in self.final_states})
            else:
                prev_level = self._word_cache[i - 1]
                level.update(
                    {
                        state: [
                            symbol + word
                            for symbol in sorted_transition_symbols[state]
                            for word in prev_level[self.transitions[state][symbol]]
                        ]
                        for state in self.states
                    }
                )

    @cached_method
    def cardinality(self) -> int:
        """
        Returns the cardinality of the language represented by the DFA.

        Returns
        ------
        int
            The cardinality of the language accepted by self.

        Raises
        ------
        InfiniteLanguageException
            Raised if self accepts an infinite language.
        """
        try:
            i = self.minimum_word_length()
        except exceptions.EmptyLanguageException:
            return 0
        limit = self.maximum_word_length()
        if limit is None:
            raise exceptions.InfiniteLanguageException(
                "The language represented by the DFA is infinite."
            )
        return sum(self.count_words_of_length(j) for j in range(i, limit + 1))

    @cached_method
    def minimum_word_length(self) -> int:
        """
        Returns the length of the shortest word in the language accepted by the DFA.

        Returns
        ------
        int
            The length of the shortest word accepted by self.

        Raises
        ------
        EmptyLanguageException
            Raised if self accepts an empty language.
        """
        queue: Deque[DFAStateT] = deque()
        distances: Dict[DFAStateT, int] = {self.initial_state: 0}
        queue.append(self.initial_state)
        while queue:
            state = queue.popleft()
            if state in self.final_states:
                return distances[state]
            for next_state in self.transitions[state].values():
                if next_state not in distances:
                    distances[next_state] = distances[state] + 1
                    queue.append(next_state)
        raise exceptions.EmptyLanguageException(
            "The language represented by the DFA is empty"
        )

    @cached_method
    def maximum_word_length(self) -> Optional[int]:
        """
        Returns the length of the longest word in the language accepted by the DFA
        In the case of infinite languages, `None` is returned.

        Returns
        ------
        Optional[int]
            The length of the longest word accepted by self. None if the language
            is infinite.

        Raises
        ------
        EmptyLanguageException
            Raised if self accepts the empty language.
        """
        if self.isempty():
            raise exceptions.EmptyLanguageException(
                "The language represented by the DFA is empty"
            )
        graph = self._get_digraph()

        accessible_nodes = get_reachable_nodes(graph, [self.initial_state])
        coaccessible_nodes = get_reachable_nodes(
            graph, self.final_states, reversed=True
        )

        important_nodes = accessible_nodes.intersection(coaccessible_nodes)
        subgraph = graph.subgraph(important_nodes)
        try:
            return nx.dag_longest_path_length(subgraph)
        except nx.exception.NetworkXUnfeasible:
            return None

    @classmethod
    def from_prefix(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        prefix: str,
        *,
        contains: bool = True,
        as_partial: bool = True,
    ) -> Self:
        """
        Directly computes the minimal DFA accepting strings with the
        given prefix. If `contains` is set to `False` then the complement is
        constructed instead.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        prefix : str
            The prefix of strings that are accepted by this DFA.
        contains : bool, default: True
            Whether or not to construct the compliment DFA.
        as_partial : bool, default: True
            Whether or not to construct this DFA as a partial DFA.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        last_state = len(prefix)
        transitions = {i: {char: i + 1} for i, char in enumerate(prefix)}
        transitions[last_state] = {symbol: last_state for symbol in input_symbols}

        # Can't construct this as a partial if we need to take the complement
        if not as_partial or not contains:
            err_state = -1
            for state_path in transitions.values():
                for symbol in input_symbols:
                    state_path.setdefault(symbol, err_state)
            transitions[err_state] = {symbol: err_state for symbol in input_symbols}

        states = frozenset(transitions.keys())
        final_states = {last_state}

        is_partial = any(
            len(lookup) != len(input_symbols) for lookup in transitions.values()
        )

        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
            allow_partial=is_partial,
        )

    @classmethod
    def from_suffix(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        suffix: str,
        *,
        contains: bool = True,
    ) -> Self:
        """
        Directly computes the minimal DFA recognizing strings with the
        given suffix. If `contains` is set to `False`, then the complement
        is constructed instead.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        suffix : str
            The suffix of strings that are accepted by this DFA.
        contains : bool, default: True
            Whether or not to construct the compliment DFA.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        return cls.from_substring(
            input_symbols, suffix, contains=contains, must_be_suffix=True
        )

    @classmethod
    def from_substring(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        substring: str,
        *,
        contains: bool = True,
        must_be_suffix: bool = False,
    ) -> Self:
        """
        Directly computes the minimal DFA recognizing strings containing the
        given substring. If `contains` is set to `False` then the complement
        is constructed instead. If `must_be_suffix` is set to `True`, then
        the substring must be a suffix instead.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        substring : str
            The substring of strings that are accepted by this DFA.
        contains : bool, default: True
            Whether or to construct the compliment DFA.
        must_be_suffix : bool, default: False
            Whether or not the target substring must be a suffix.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        transitions: Dict[DFAStateT, Dict[str, DFAStateT]] = {
            i: {} for i in range(len(substring))
        }
        transitions[len(substring)] = {
            symbol: len(substring) for symbol in input_symbols
        }

        # Computing failure function for partial matches as is done in the
        # Knuth-Morris-Pratt string algorithm so we can quickly compute the
        # next state from another state
        # This table only holds integers, so array.array is used to save memory.
        kmp_table = array.array("i", (-1 for _ in substring))
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

        limit = len(substring) + 1 if must_be_suffix else len(substring)
        for i in range(limit):
            prefix_dict = transitions.setdefault(i, {})
            for symbol in input_symbols:
                # Look for next state after reading in the given input symbol
                candidate = i if i < len(substring) else kmp_table[i]
                while candidate != -1 and substring[candidate] != symbol:
                    candidate = kmp_table[candidate]
                candidate += 1
                prefix_dict[symbol] = candidate

        states = frozenset(transitions.keys())
        final_states = {len(substring)}
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
        )

    @classmethod
    def from_substrings(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        substrings: AbstractSet[str],
        *,
        contains: bool = True,
        must_be_suffix: bool = False,
    ) -> Self:
        """
        Directly computes a DFA recognizing strings containing at least one of the
        given substrings. The implementation is based on the Aho-Corasick
        string-searching algorithm. If `contains` is set to `False`, then the
        complement is constructed instead. If `must_be_suffix` is set to `True`,
        then the each substring must be a suffix instead.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        substrings : str
            The set of strings to be recognized by this DFA.
        contains : bool, default: True
            Whether or to construct the compliment DFA.
        must_be_suffix : bool, default: False
            Whether or not the target substrings must be a suffix.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """

        class OutNode:
            def __init__(self, keyword: str, next_node: Optional[OutNode]) -> None:
                self.keyword: str = keyword
                self.successor: Optional[OutNode] = next_node

        class Node:
            def __init__(self) -> None:
                self.out: Optional[OutNode] = None
                self.fail: Optional[Node] = None
                self.successors: Dict[str, Node] = {}

        root = Node()
        labels = {id(root): 0}
        final_states = set()
        for substring in substrings:
            current_node = root
            for symbol in substring:
                current_node.successors.setdefault(symbol, Node())
                current_node = current_node.successors[symbol]
                labels.setdefault(id(current_node), len(labels))
            current_node.out = OutNode(substring, None)

        queue = deque(root.successors.values())
        while queue:
            current_node = queue.popleft()
            for symbol, successor in current_node.successors.items():
                queue.append(successor)

                st = current_node.fail
                while st is not None and symbol not in st.successors:
                    st = st.fail

                if st is None:
                    st = root

                successor.fail = st.successors.get(symbol, None)

                if successor.fail is not None:
                    if successor.out is None:
                        successor.out = successor.fail.out
                    else:
                        out = successor.out
                        while out.successor is not None:
                            out = out.successor
                        out.successor = successor.fail.out

        transitions: Dict[DFAStateT, Dict[str, DFAStateT]] = {}

        queue = deque([root])
        while queue:
            current_node = queue.popleft()
            state = labels[id(current_node)]
            if current_node.out is not None:
                final_states.add(state)
            current_transitions = {}
            for symbol in input_symbols:
                if symbol in current_node.successors:
                    queue.append(current_node.successors[symbol])
                parent_node: Optional[Node] = current_node
                while parent_node is not None and symbol not in parent_node.successors:
                    parent_node = parent_node.fail
                if parent_node is None:
                    parent_node = root
                successor = parent_node.successors.get(symbol, root)
                current_transitions[symbol] = labels[id(successor)]

            transitions[state] = current_transitions

        if not must_be_suffix:
            end_state = len(transitions)
            transitions[end_state] = {symbol: end_state for symbol in input_symbols}
            for state in final_states:
                transitions[state] = {symbol: end_state for symbol in input_symbols}
            final_states.add(end_state)

        states = frozenset(transitions.keys())
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
        )

    @classmethod
    def from_subsequence(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        subsequence: str,
        *,
        contains: bool = True,
    ) -> Self:
        """
        Directly computes the minimal DFA recognizing strings containing the
        given subsequence. If `contains` is set to `False`, then the complement
        is constructed instead.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        subsequence : str
            The target subsequence of strings that are accepted by this DFA.
        contains : bool, default: True
            Whether or to construct the compliment DFA.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        transitions = {0: {symbol: 0 for symbol in input_symbols}}

        for prev_state, char in enumerate(subsequence):
            next_state = prev_state + 1
            transitions[next_state] = {symbol: next_state for symbol in input_symbols}
            transitions[prev_state][char] = next_state

        states = frozenset(transitions.keys())
        final_states = {len(subsequence)}
        return cls(
            states=states,
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states if contains else states - final_states,
        )

    @classmethod
    def of_length(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        *,
        min_length: int = 0,
        max_length: Optional[int] = None,
        symbols_to_count: Optional[AbstractSet[str]] = None,
    ) -> Self:
        """
        Directly computes the minimal DFA recognizing strings whose length is
        between `min_length` and `max_length`, inclusive. To allow arbitrarily
        long words, the value `None` can be passed in for `max_length`.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        min_length : int, default: 0
            The minimum length of strings to be accepted by this DFA.
        max_length : Optional[int], default: None
            The maximum length of strings to be accepted by this DFA.
            If set to None, there is no maximum.
        symbols_to_count : Optional[AbstractSet[str]], default: None
            The input symbols to count towards the length of words to accepts.
            If set to None, counts all symbols.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        if symbols_to_count is None:
            symbols_to_count = input_symbols

        transitions = {}
        length_range = (
            range(min_length) if max_length is None else range(max_length + 1)
        )
        for prev_state in length_range:
            next_state = prev_state + 1
            transitions[prev_state] = {
                symbol: next_state if symbol in symbols_to_count else prev_state
                for symbol in input_symbols
            }
        last_state = len(transitions)
        transitions[last_state] = {symbol: last_state for symbol in input_symbols}
        final_states = (
            frozenset((last_state,))
            if max_length is None
            else frozenset(range(min_length, max_length + 1))
        )

        return cls(
            states=frozenset(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=final_states,
        )

    @classmethod
    def count_mod(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        k: int,
        *,
        remainders: Optional[AbstractSet[int]] = None,
        symbols_to_count: Optional[AbstractSet[str]] = None,
    ) -> Self:
        """
        Directly computes a DFA that counts given symbols and accepts all strings where
        the remainder of division by k is in the set of remainders given.
        The default value of remainders is {0} and all symbols are counted by default.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        k : int
            The number to divide the length by.
        remainders : Optional[AbstractSet[int]], default: None
            The remainders to accept. If set to None, defaults to {0}.
        symbols_to_count : Optional[AbstractSet[str]], default: None
            The input symbols to count towards the length of words to accepts.
            If set to None, counts all symbols.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        if k <= 0:
            raise ValueError("Integer must be positive")
        if symbols_to_count is None:
            symbols_to_count = input_symbols
        if remainders is None:
            remainders = {0}
        transitions = {
            i: {
                symbol: (i + 1) % k if symbol in symbols_to_count else i
                for symbol in input_symbols
            }
            for i in range(k)
        }

        return cls(
            states=frozenset(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states=remainders,
        )

    @classmethod
    def universal_language(cls: Type[Self], input_symbols: AbstractSet[str]) -> Self:
        """
        Directly computes the minimal DFA accepting all strings.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        return cls(
            states={0},
            input_symbols=input_symbols,
            transitions={0: {symbol: 0 for symbol in input_symbols}},
            initial_state=0,
            final_states={0},
            allow_partial=False,
        )

    @classmethod
    def empty_language(cls: Type[Self], input_symbols: AbstractSet[str]) -> Self:
        """
        Directly computes the minimal DFA rejecting all strings.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        return cls(
            states={0},
            input_symbols=input_symbols,
            transitions={0: {symbol: 0 for symbol in input_symbols}},
            initial_state=0,
            final_states=frozenset(),
            allow_partial=False,
        )

    @classmethod
    def nth_from_start(
        cls: Type[Self], input_symbols: AbstractSet[str], symbol: str, n: int
    ) -> Self:
        """
        Directly computes the minimal DFA which accepts all words whose `n`th
        character from the start is `symbol`, where `n` is a positive integer.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        symbol : str
            The target input symbol.
        n : int
            The position of the target input symbol.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        if n < 1:
            raise ValueError("Integer must be positive")
        if symbol not in input_symbols:
            raise exceptions.InvalidSymbolError(
                "Desired symbol is not in the set of input symbols"
            )
        if len(input_symbols) == 1:
            return cls.of_length(input_symbols, min_length=n)
        transitions = {i: {symbol: i + 1 for symbol in input_symbols} for i in range(n)}
        transitions[n - 1][symbol] = n + 1
        transitions[n] = {symbol: n for symbol in input_symbols}
        transitions[n + 1] = {symbol: n + 1 for symbol in input_symbols}

        return cls(
            states=frozenset(transitions.keys()),
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state=0,
            final_states={n + 1},
            allow_partial=False,
        )

    @classmethod
    def nth_from_end(
        cls: Type[Self], input_symbols: AbstractSet[str], symbol: str, n: int
    ) -> Self:
        """
        Directly computes the minimal DFA which accepts all words whose `n`th
        character from the end is `symbol`, where `n` is a positive integer.

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        symbol : str
            The target input symbol.
        n : int
            The position of the target input symbol.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """
        if n < 1:
            raise ValueError("Integer must be positive")
        if symbol not in input_symbols:
            raise exceptions.InvalidSymbolError(
                "Desired symbol is not in the set of input symbols"
            )
        if len(input_symbols) == 1:
            return cls.of_length(input_symbols, min_length=n)
        # Consider the states to be labelled with bitstrings of size n The
        # bitstring represents how the current suffix in this state matches our
        # desired symbol A 1 means the character at this position is the desired
        # symbol and a 0 means it is not For transitions this is effectively
        # doubling the label value and then adding 1 if the desired symbol is
        # read Finally we trim the label to n bits with a modulo operation.
        state_count = 2**n

        return cls(
            states=frozenset(range(state_count)),
            input_symbols=input_symbols,
            transitions={
                state: {
                    sym: (
                        (2 * state + 1) % state_count
                        if symbol == sym
                        else (2 * state) % state_count
                    )
                    for sym in input_symbols
                }
                for state in range(state_count)
            },
            initial_state=0,
            final_states=frozenset(range(state_count // 2, state_count)),
            allow_partial=False,
        )

    @classmethod
    def from_finite_language(
        cls: Type[Self],
        input_symbols: AbstractSet[str],
        language: AbstractSet[str],
        as_partial: bool = True,
    ) -> Self:
        """
        Directly computes the minimal DFA accepting the finite language given as input.
        Uses the algorithm described in Finite-State Techniques by Mihov and Schulz,
        Chapter 10

        Parameters
        ----------
        input_symbols : AbstractSet[str]
            The set of input symbols to construct the DFA over.
        language : AbstractSet[str]
            The language to accept.
        as_partial : bool, default: True
            Whether or not to construct this as a partial DFA.

        Returns
        ------
        Self
            The DFA accepting the desired language.
        """

        SignatureT: TypeAlias = Tuple[bool, FrozenSet[Tuple[str, str]]]

        if not language:
            return cls.empty_language(input_symbols)

        transitions: Dict[DFAStateT, Dict[str, DFAStateT]] = {}
        back_map: Dict[str, Set[str]] = {"": set()}
        final_states: Set[str] = set()
        signatures_dict: Dict[SignatureT, str] = {}

        def compute_signature(state: str) -> SignatureT:
            """Computes signature for input state"""
            return (state in final_states, frozenset(transitions[state].items()))

        def longest_common_prefix_length(string_1: str, string_2: str) -> int:
            """Returns length of longest common prefix."""
            for i, (symbol_1, symbol_2) in enumerate(zip(string_1, string_2)):
                if symbol_1 != symbol_2:
                    return i

            return min(len(string_1), len(string_2))

        def add_to_trie(word: str) -> None:
            """Add word to the trie represented by transitions"""
            prefix = ""
            for symbol in word:
                next_prefix = prefix + symbol

                # Extend the trie only if necessary
                prefix_dict = transitions.setdefault(prefix, {})
                prefix_dict.setdefault(symbol, next_prefix)
                back_map.setdefault(next_prefix, set()).add(prefix)

                prefix = next_prefix

            # Mark the finished prefix as a final state
            transitions[prefix] = {}
            final_states.add(prefix)

        def compress(word: str, next_word: str) -> None:
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
                        for symbol in path:
                            if path[symbol] == prefix:
                                path[symbol] = identical_state
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

        compress(prev_word, "")

        if as_partial:
            return cls(
                states=frozenset(transitions.keys()),
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state="",
                final_states=final_states,
                allow_partial=as_partial,
            )

        return cls._to_complete(
            input_symbols=input_symbols,
            transitions=transitions,
            initial_state="",
            final_states=final_states,
            trap_state=0,
        )

    @classmethod
    def from_nfa(
        cls: Type[Self],
        target_nfa: nfa.NFA,
        *,
        retain_names: bool = False,
        minify: bool = True,
    ) -> Self:
        """
        Initialize this DFA as one equivalent to the given NFA. Note
        that this usually returns a partial DFA by default.

        Parameters
        ----------
        target_nfa : NFA
            The NFA to construct an equivalent DFA for.
        retain_names : bool, default: False
            Whether or not to retain state names during processing.
        minify : bool, default: True
            Whether or not to minify the DFA resulting from the input NFA.

        Returns
        ------
        Self
            The DFA accepting the language of the input NFA.
        """

        def subset_function(current_states: FrozenSet[DFAStateT]) -> bool:
            return not current_states.isdisjoint(target_nfa.final_states)

        initial_state = frozenset(
            target_nfa._get_lambda_closures()[target_nfa.initial_state]
        )

        return cls._expand_dfa(
            subset_function,
            initial_state,
            target_nfa._iterate_through_symbol_path_pairs,
            target_nfa.input_symbols,
            retain_names=retain_names,
            minify=minify,
        )

    def iter_transitions(
        self,
    ) -> Generator[Tuple[DFAStateT, DFAStateT, str], None, None]:
        """
        Iterate over all transitions in the DFA. Each transition is a tuple
        of the form (from_state, to_state, symbol).

        Returns
        ------
        Generator[Tuple[DFAStateT, DFAStateT, str], None, None]
            The desired generator over the DFA transitions.
        """
        return (
            (from_, to_, symbol)
            for from_, lookup in self.transitions.items()
            for symbol, to_ in lookup.items()
        )

    def _get_input_path(
        self, input_str: str
    ) -> Tuple[List[Tuple[DFAStateT, DFAStateT, DFASymbolT]], bool]:
        """
        Calculate the path taken by input.

        Parameters
        ------
        input_str : str
            The input string to run on the DFA.

        Returns
        ------
        Tuple[List[Tuple[DFAStateT, DFAStateT, DFASymbolT], bool]]
            A list of all transitions taken in each step and a boolean
            indicating whether the DFA accepted the input.

        """

        state_history = list(self.read_input_stepwise(input_str, ignore_rejection=True))

        path = [
            (*state_pair, char)
            for state_pair, char in zip(pairwise(state_history), input_str)
        ]

        last_state = state_history[-1] if state_history else self.initial_state
        accepted = last_state in self.final_states

        return path, accepted
