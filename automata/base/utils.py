#!/usr/bin/env python3
"""Miscellaneous utility functions and classes."""

import os
import pathlib
import random
import uuid
from collections import defaultdict
from itertools import count, tee, zip_longest
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Set,
    Tuple,
    TypeAlias,
    TypeVar,
    Union,
)

from frozendict import frozendict

# Optional imports for use with visual functionality
try:
    import pygraphviz as pgv
except ImportError:
    _visual_imports = False
else:
    _visual_imports = True
finally:
    # create a type for type checker
    # irrespective of whether the imports were successful
    GraphT: TypeAlias = "pgv.AGraph"


LayoutMethod = Literal["neato", "dot", "twopi", "circo", "fdp", "nop"]


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

    return defaultdict(counter.__next__).__getitem__


def create_unique_random_id() -> str:
    # To be able to set the random seed, took code from:
    # https://nathanielknight.ca/articles/consistent_random_uuids_in_python.html
    return str(
        uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)
    )


def create_graph(
    horizontal: bool = True,
    reverse_orientation: bool = False,
    fig_size: Union[Tuple[float, float], Tuple[float], None] = None,
    state_separation: float = 0.5,
) -> GraphT:
    """Creates and returns a graph object
    Args:
        - horizontal (bool, optional): Direction of node layout. Defaults
            to True.
        - reverse_orientation (bool, optional): Reverse direction of node
            layout. Defaults to False.
        - fig_size (tuple, optional): Figure size. Defaults to None.
        - state_separation (float, optional): Node distance. Defaults to 0.5.
    Returns:
        AGraph with the given configuration.
    """
    if not _visual_imports:
        raise ImportError(
            "Missing visualization packages; "
            "please install coloraide and pygraphviz."
        )

    # Defining the graph.
    graph = pgv.AGraph(strict=False, directed=True)

    if fig_size is not None:
        graph.graph_attr.update(size=", ".join(map(str, fig_size)))

    graph.graph_attr.update(ranksep=str(state_separation))

    if horizontal:
        rankdir = "RL" if reverse_orientation else "LR"
    else:
        rankdir = "BT" if reverse_orientation else "TB"

    graph.graph_attr.update(rankdir=rankdir)

    return graph


def save_graph(
    graph: GraphT,
    path: Union[str, os.PathLike],
) -> None:
    """Write `graph` to file given by `path`. PNG, SVG, etc.
    Returns the same graph."""

    save_path_final: pathlib.Path = pathlib.Path(path)

    format = save_path_final.suffix.split(".")[1] if save_path_final.suffix else None

    graph.draw(
        path=save_path_final,
        format=format,
    )


T = TypeVar("T")


class PartitionRefinement(Generic[T]):
    """Maintain and refine a partition of a set of items into subsets.
    Space usage for a partition of n items is O(n), and each refine operation
    takes time proportional to the size of its argument.

    Adapted from code by D. Eppstein:
    https://www.ics.uci.edu/~eppstein/PADS/PartitionRefinement.py
    """

    __slots__: Tuple[str, ...] = ("_sets", "_partition")

    _sets: Dict[int, Set[T]]
    _partition: Dict[T, int]

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

            # Only need to check lengths, we already know AintS is a subset of A
            # by construction
            if len(AintS) < len(A):
                self._sets[id(AintS)] = AintS
                for x in AintS:
                    self._partition[x] = id(AintS)
                A -= AintS
                output.append((id(AintS), Aid))

        return output


def pairwise(iterable: Iterable[T], final_none: bool = False) -> Iterable[Tuple[T, T]]:
    """Based on https://docs.python.org/3/library/itertools.html#itertools.pairwise"""
    a, b = tee(iterable)
    next(b, None)

    if final_none:
        return zip_longest(a, b)

    return zip(a, b)
