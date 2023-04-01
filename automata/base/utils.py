#!/usr/bin/env python3
"""Miscellaneous utility functions and classes."""

from collections import defaultdict

from frozendict import frozendict
from typing import (
    Any,
    Callable,
    Tuple,
    Iterable,
    Generic,
    TypeVar,
    Set,
    Dict,
    List,
    DefaultDict,
)
from itertools import count


def freeze_value(value: Any) -> Any:
    """
    A helper function to convert the given value / structure into a fully
    immutable one by recursively processing said structure and any of its
    members, freezing them as well
    """
    if isinstance(value, (str, int)):
        return value
    if isinstance(value, dict):
        return frozendict(
            {
                dict_key: freeze_value(dict_value)
                for dict_key, dict_value in value.items()
            }
        )
    if isinstance(value, set):
        return frozenset(freeze_value(element) for element in value)
    if isinstance(value, list):
        return tuple(freeze_value(element) for element in value)
    return value


def get_renaming_function(counter: count) -> Callable[[Any], int]:
    """
    A helper function that returns a renaming function to be used in the creation of
    other automata. The parameter counter should be an itertools count.
    This helper function will return the same distinct output taken from counter
    for each distinct input.
    """

    new_state_name_dict: DefaultDict[Any, int] = defaultdict(lambda: next(counter))

    def renaming_function(item: Any) -> int:
        return new_state_name_dict[item]

    return renaming_function


T = TypeVar("T")


class PartitionRefinement(Generic[T]):
    """Maintain and refine a partition of a set of items into subsets.
    Space usage for a partition of n items is O(n), and each refine
    operation takes time proportional to the size of its argument.

    Adapted from code by D. Eppstein: https://www.ics.uci.edu/~eppstein/PADS/PartitionRefinement.py
    """

    __slots__: Tuple[str, ...] = ("_sets", "_partition")

    def __init__(self, items: Iterable[T]) -> None:
        """Create a new partition refinement data structure for the given
        items. Initially, all items belong to the same subset.
        """
        S = set(items)
        self._sets = {id(S): S}
        self._partition = {x: id(S) for x in S}

    def get_set_by_id(self, id: int) -> Set[T]:
        """Return the set in the partition corresponding to id."""
        return self._sets[id]

    def get_set_ids(self) -> Iterable[int]:
        """Return set ids corresponding to the internal partition."""
        return self._sets.keys()

    def get_sets(self) -> Iterable[Set[T]]:
        """Return sets corresponding to the internal partition."""
        return self._sets.values()

    def refine(self, S: Iterable[T]) -> List[Tuple[int, int]]:
        """Refine each set A in the partition to the two sets
        A & S, A - S.  Return a list of pairs ids (id(A & S), id(A - S))
        for each changed set.  Within each pair, A & S will be
        a newly created set, while A - S will be a modified
        version of an existing set in the partition (retaining its old id).
        Not a generator because we need to perform the partition
        even if the caller doesn't iterate through the results.
        """
        hit = defaultdict(set)
        output = []

        for x in S:
            hit[self._partition[x]].add(x)

        for Aid, AintS in hit.items():
            A = self._sets[Aid]

            # Only need to check lengths, we already know AintS is a subset of A by construction
            if len(AintS) < len(A):
                self._sets[id(AintS)] = AintS
                for x in AintS:
                    self._partition[x] = id(AintS)
                A -= AintS
                output.append((id(AintS), Aid))

        return output
