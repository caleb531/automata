"""Shared fixtures and utilities for DFA tests."""

import tempfile
from itertools import permutations
from typing import Iterable, Tuple, TypeVar, cast

import tests.test_fa as test_fa
from automata.fa.dfa import DFA

ArgT = TypeVar("ArgT")


def get_permutation_tuples(*args: ArgT) -> Tuple[Tuple[ArgT, ArgT], ...]:
    """Return a tuple of ordered argument pairs for permutation-based tests."""
    return tuple(cast(Iterable[Tuple[ArgT, ArgT]], permutations(args, 2)))


class DFATestCase(test_fa.TestFA):
    """Base test case providing common DFA fixtures."""

    temp_dir_path = tempfile.gettempdir()

    # A partial DFA that accepts the string "111" only
    partial_dfa = DFA(
        states=set(range(4)),
        input_symbols={"0", "1"},
        transitions={
            0: {"1": 1},
            1: {"1": 2},
            2: {"1": 3},
            3: {},
        },
        initial_state=0,
        final_states={3},
        allow_partial=True,
    )

    # This DFA accepts all words which do not contain two consecutive occurrences of 1
    no_consecutive_11_dfa = DFA(
        states={"p0", "p1", "p2"},
        input_symbols={"0", "1"},
        transitions={
            "p0": {"0": "p0", "1": "p1"},
            "p1": {"0": "p0", "1": "p2"},
            "p2": {"0": "p2", "1": "p2"},
        },
        initial_state="p0",
        final_states={"p0", "p1"},
    )

    # This DFA accepts all words which contain at least four occurrences of 1
    at_least_four_ones = DFA(
        states={"q0", "q1", "q2", "q3", "q4"},
        input_symbols={"0", "1"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q1", "1": "q2"},
            "q2": {"0": "q2", "1": "q3"},
            "q3": {"0": "q3", "1": "q4"},
            "q4": {"0": "q4", "1": "q4"},
        },
        initial_state="q0",
        final_states={"q4"},
    )

    # This DFA accepts all words which contain either zero or one occurrence of 1
    zero_or_one_1_dfa = DFA(
        states={"q0", "q1", "q2"},
        input_symbols={"0", "1"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q1", "1": "q2"},
            "q2": {"0": "q2", "1": "q2"},
        },
        initial_state="q0",
        final_states={"q0", "q1"},
    )

    # This DFA has no reachable final states and therefore is finite
    no_reachable_final_dfa = DFA(
        states={"q0", "q1", "q2", "q3"},
        input_symbols={"0", "1"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q1", "1": "q2"},
            "q2": {"0": "q0", "1": "q1"},
            "q3": {"0": "q2", "1": "q1"},
        },
        initial_state="q0",
        final_states={"q3"},
    )
