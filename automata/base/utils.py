#!/usr/bin/env python3
"""Miscellaneous utility functions and classes."""

from frozendict import frozendict


def freezeValue(value):
    """
    A helper function to convert the given value / structure into a fully
    immutable one by recursively processing said structure and any of its
    members, freezing them as well
    """
    if isinstance(value, list):
        return tuple(freezeValue(element) for element in value)
    if isinstance(value, set):
        return frozenset(freezeValue(element) for element in value)
    elif isinstance(value, dict):
        return frozendict({
            dict_key: freezeValue(dict_value)
            for dict_key, dict_value in value.items()
        })
    else:
        return value


class PartitionRefinement:
    """Maintain and refine a partition of a set of items into subsets.
    Space usage for a partition of n items is O(n), and each refine
    operation takes time proportional to the size of its argument.

    Adapted from code by D. Eppstein: https://www.ics.uci.edu/~eppstein/PADS/PartitionRefinement.py
    """

    __slots__ = ["_sets", "_partition"]

    def __init__(self, items):
        """Create a new partition refinement data structure for the given
        items. Initially, all items belong to the same subset.
        """
        S = set(items)
        self._sets = {id(S): S}
        self._partition = {x: id(S) for x in S}

    def get_set_by_id(self, id):
        """Return the set in the partition corresponding to id."""
        return self._sets[id]

    def get_set_ids(self):
        """Return set ids corresponding to the internal partition."""
        return self._sets.keys()

    def get_sets(self):
        """Return sets corresponding to the internal partition."""
        return self._sets.values()

    def refine(self, S):
        """Refine each set A in the partition to the two sets
        A & S, A - S.  Return a list of pairs ids (id(A & S), id(A - S))
        for each changed set.  Within each pair, A & S will be
        a newly created set, while A - S will be a modified
        version of an existing set in the partition (retaining its old id).
        Not a generator because we need to perform the partition
        even if the caller doesn't iterate through the results.
        """
        hit = {}
        output = []

        for x in S:
            Aid = self._partition[x]
            hit.setdefault(Aid, set()).add(x)

        for Aid, AS in hit.items():
            A = self._sets[Aid]
            if AS != A:
                self._sets[id(AS)] = AS
                for x in AS:
                    self._partition[x] = id(AS)
                A -= AS
                output.append((id(AS), Aid))

        return output
