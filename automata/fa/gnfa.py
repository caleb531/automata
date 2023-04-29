#!/usr/bin/env python3
"""Classes and methods for working with generalized non-deterministic finite
automata."""
from __future__ import annotations

from functools import cached_property
from itertools import product
from typing import (
    AbstractSet,
    Dict,
    Generator,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)

from frozendict import frozendict
from typing_extensions import NoReturn, Self

import automata.base.exceptions as exceptions
import automata.fa.dfa as dfa
import automata.fa.fa as fa
import automata.fa.nfa as nfa
import automata.regex.regex as re

GNFAStateT = fa.AutomatonStateT

GNFAPathT = Mapping[GNFAStateT, Optional[str]]
GNFATransitionsT = Mapping[GNFAStateT, GNFAPathT]


class GNFA(fa.FA):
    """A generalized nondeterministic finite automaton."""

    __slots__ = (
        "states",
        "input_symbols",
        "transitions",
        "initial_state",
        "final_state",
        "__dict__",
    )

    final_state: GNFAStateT

    def __init__(
        self,
        *,
        states: AbstractSet[GNFAStateT],
        input_symbols: AbstractSet[str],
        transitions: GNFATransitionsT,
        initial_state: GNFAStateT,
        final_state: GNFAStateT,
    ) -> None:
        """Initialize a complete NFA."""
        super(fa.FA, self).__init__(
            states=frozenset(states),
            input_symbols=frozenset(input_symbols),
            transitions=frozendict(
                {state: frozendict(paths) for state, paths in transitions.items()}
            ),
            initial_state=initial_state,
            final_state=final_state,
        )

    # GNFA should NOT create the lambda closures via NFA.__post_init__()
    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dfa(cls: Type[Self], dfa: dfa.DFA) -> Self:
        """Initialize this GNFA as one equivalent to the given DFA."""
        new_gnfa_transitions = dict()
        gnfa_states = set(dfa.states)

        for state in dfa.states:
            gnfa_transitions: Dict[GNFAStateT, Optional[str]] = dict()
            if state in dfa.transitions:
                for input_symbol, to_state in dfa.transitions[state].items():
                    if to_state in gnfa_transitions.keys():
                        gnfa_transitions[
                            to_state
                        ] = f"{gnfa_transitions[to_state]}|{input_symbol}"
                    else:
                        gnfa_transitions[to_state] = input_symbol
                new_gnfa_transitions[state] = gnfa_transitions
            else:
                new_gnfa_transitions[state] = dict()

        new_initial_state = GNFA._add_new_state(gnfa_states)
        new_final_state = GNFA._add_new_state(gnfa_states, new_initial_state)

        new_gnfa_transitions[new_initial_state] = {dfa.initial_state: ""}

        for state in dfa.final_states:
            new_gnfa_transitions[state][new_final_state] = ""

        for state in gnfa_states - {new_final_state}:  # pragma: no branch
            if gnfa_states - new_gnfa_transitions[state].keys():  # pragma: no branch
                for leftover_state in gnfa_states - new_gnfa_transitions[state].keys():
                    if leftover_state is not new_initial_state:
                        new_gnfa_transitions[state][leftover_state] = None

        return cls(
            states=gnfa_states,
            input_symbols=dfa.input_symbols,
            transitions=new_gnfa_transitions,
            initial_state=new_initial_state,
            final_state=new_final_state,
        )

    @classmethod
    def from_nfa(cls: Type[Self], nfa: nfa.NFA) -> Self:
        """Initialize this GNFA as one equivalent to the given NFA."""
        new_gnfa_transitions: Dict[GNFAStateT, Dict[GNFAStateT, Optional[str]]] = dict()
        gnfa_states = set(nfa.states)

        for state in nfa.states:
            gnfa_transitions: Dict[GNFAStateT, str] = dict()
            if state in nfa.transitions:
                for input_symbol, to_states in nfa.transitions[state].items():
                    for to_state in to_states:
                        if to_state in gnfa_transitions.keys():
                            if gnfa_transitions[to_state] == "" and input_symbol != "":
                                gnfa_transitions[to_state] = f"{input_symbol}?"
                            elif (
                                gnfa_transitions[to_state] != "" and input_symbol == ""
                            ):
                                if cls._isbracket_req(gnfa_transitions[to_state]):
                                    gnfa_transitions[
                                        to_state
                                    ] = f"({gnfa_transitions[to_state]})?"
                                else:
                                    gnfa_transitions[
                                        to_state
                                    ] = f"{gnfa_transitions[to_state]}?"
                            else:
                                gnfa_transitions[
                                    to_state
                                ] = f"{gnfa_transitions[to_state]}|{input_symbol}"
                        else:
                            gnfa_transitions[to_state] = input_symbol
                new_gnfa_transitions[state] = cast(
                    Dict[GNFAStateT, Optional[str]], gnfa_transitions
                )
            else:
                new_gnfa_transitions[state] = dict()

        new_initial_state = GNFA._add_new_state(gnfa_states)
        new_final_state = GNFA._add_new_state(gnfa_states, new_initial_state)

        new_gnfa_transitions[new_initial_state] = {nfa.initial_state: ""}

        for state in nfa.final_states:
            new_gnfa_transitions[state][new_final_state] = ""

        for state in gnfa_states - {new_final_state}:  # pragma: no branch
            if gnfa_states - new_gnfa_transitions[state].keys():  # pragma: no branch
                for leftover_state in gnfa_states - new_gnfa_transitions[state].keys():
                    if leftover_state is not new_initial_state:
                        new_gnfa_transitions[state][leftover_state] = None

        return cls(
            states=gnfa_states,
            input_symbols=nfa.input_symbols,
            transitions=new_gnfa_transitions,
            initial_state=new_initial_state,
            final_state=new_final_state,
        )

    def _validate_transition_invalid_symbols(
        self, start_state: GNFAStateT, paths: GNFAPathT
    ) -> None:
        """Raise an error if transition symbols are invalid."""
        check = self.input_symbols | {"*", "|", "(", ")", "?"}

        for regex in paths.values():
            if regex is not None and (
                set(regex) - check and regex != "" or not re._validate(regex)
            ):
                raise exceptions.InvalidRegexError(
                    "state {} has invalid transition expression {}".format(
                        start_state, regex
                    )
                )

    def _validate_transition_end_states(
        self, start_state: GNFAStateT, paths: GNFAPathT
    ) -> None:
        """Raise an error if transition end states are invalid or missing"""
        if start_state == self.final_state:
            if len(paths) != 0:  # pragma: no branch
                raise exceptions.InvalidStateError(
                    "No transitions should be defined for "
                    "final state {}".format(start_state)
                )
        elif (
            start_state == self.initial_state
            and self.states - paths.keys() - {self.initial_state} != set()
        ):
            raise exceptions.MissingStateError(
                "state {} does not have transitions defined for states {}".format(
                    start_state, str(self.states - paths.keys() - {self.initial_state})
                )
            )
        elif (
            start_state != self.initial_state
            and self.states - paths.keys() - {self.initial_state} != set()
        ):
            raise exceptions.MissingStateError(
                "state {} does not have transitions defined for states {}".format(
                    start_state, str(self.states - paths.keys() - {self.initial_state})
                )
            )
        for end_state in paths.keys():  # pragma: no branch
            if end_state not in self.states:
                raise exceptions.InvalidStateError(
                    "end state {} for transition on {} is "
                    "not valid".format(end_state, start_state)
                )

    def _validate_final_state(self) -> None:
        """Raise an error if the initial state is invalid."""
        if self.final_state not in self.states:
            raise exceptions.InvalidStateError(
                "{} is not a valid final state".format(self.final_state)
            )

    def validate(self) -> None:
        """Return True if this NFA is internally consistent."""
        self._validate_initial_state()
        self._validate_final_state()
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
            self._validate_transition_end_states(start_state, paths)
        self._validate_initial_state_transitions()

    @staticmethod
    def _isbracket_req(regex: str) -> bool:
        bracket_open = 0
        for symbol in regex:
            if symbol == "(":
                bracket_open += 1
            elif symbol == ")":
                bracket_open -= 1
            if bracket_open == 0 and symbol == "|":
                return True

        return False

    @staticmethod
    def _find_min_connected_node(
        states: Set[GNFAStateT],
        transitions: GNFATransitionsT,
        initial_state: GNFAStateT,
        final_state: GNFAStateT,
    ) -> GNFAStateT:
        state_set = states - {initial_state, final_state}
        state_degree = dict.fromkeys(state_set, 0)

        for state in states - {final_state}:
            for to_state, label in transitions[state].items():
                if label is not None:
                    if state != initial_state:
                        state_degree[state] += 1
                    if to_state != final_state:
                        state_degree[to_state] += 1

        return min(state_degree, key=lambda x: state_degree.get(x, -1))

    def to_regex(self) -> str:
        """
        Convert GNFA to regular expression.
        """
        new_states = set(self.states)
        new_transitions = {
            state: dict(paths) for state, paths in self.transitions.items()
        }

        while len(new_states) > 2:
            q_rip = self._find_min_connected_node(
                new_states, new_transitions, self.initial_state, self.final_state
            )
            new_states.remove(q_rip)
            for q_i, q_j in product(
                new_states - {self.final_state}, new_states - {self.initial_state}
            ):
                r1 = new_transitions[q_i][q_rip]
                r2 = new_transitions[q_rip][q_rip]
                r3 = new_transitions[q_rip][q_j]
                r4 = new_transitions[q_i][q_j]

                if r1 is None or r3 is None:
                    new_transitions[q_i][q_j] = r4
                else:
                    # check if putting brackets around r1 is necessary
                    if self._isbracket_req(r1):
                        r1 = f"({r1})"

                    if r2 is None:
                        r2 = ""
                    elif len(r2) == 1:
                        r2 = f"{r2}*"
                    else:
                        r2 = f"({r2})*"

                    if self._isbracket_req(r3):
                        r3 = f"({r3})"

                    if r4 is None:
                        r4 = ""
                    elif self._isbracket_req(r4):
                        r4 = f"|({r4})"
                    elif r4 == "":
                        r4 = "?"
                    else:
                        r4 = f"|{r4}"

                    if r4 == "?" and len(r1) + len(r2) + len(r3) > 1:
                        new_transitions[q_i][q_j] = f"({r1}{r2}{r3}){r4}"
                    else:
                        new_transitions[q_i][q_j] = f"{r1}{r2}{r3}{r4}"

            del new_transitions[q_rip]
            for state in new_states - {self.final_state}:
                del new_transitions[state][q_rip]

        return new_transitions[self.initial_state][self.final_state]

    def read_input_stepwise(self, input_str: str) -> NoReturn:
        raise NotImplementedError

    def iter_transitions(
        self,
    ) -> Generator[Tuple[GNFAStateT, GNFAStateT, str], None, None]:
        return (
            (from_, to_, symbol)
            for from_, lookup in self.transitions.items()
            for to_, symbol in lookup.items()
            if symbol is not None
        )

    @cached_property
    def final_states(self):
        return frozenset({self.final_state})

    def _get_input_path(self, input_str: str) -> NoReturn:
        raise NotImplementedError(
            f"_get_input_path is not implemented for {self.__class__}"
        )
