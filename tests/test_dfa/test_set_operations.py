"""Tests covering DFA equivalence checks and set-theoretic operations."""

from parameterized import parameterized  # type: ignore

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from tests.test_dfa.base import DfaTestCase, get_permutation_tuples


class TestDfaEquivalence(DfaTestCase):
    """Validate DFA equality and conversions between partial and complete forms."""

    def test_equivalence_not_equal(self) -> None:
        self.assertNotEqual(self.no_consecutive_11_dfa, self.zero_or_one_1_dfa)

    def test_equivalence_partials(self) -> None:
        complete_dfa = self.partial_dfa.to_complete()
        self.assertEqual(self.partial_dfa, self.partial_dfa)
        self.assertEqual(self.partial_dfa, complete_dfa)
        self.assertEqual(self.partial_dfa, complete_dfa.to_partial(minify=False))

        test_dfa = DFA(
            states=complete_dfa.states,
            input_symbols=complete_dfa.input_symbols,
            transitions=complete_dfa.transitions,
            initial_state=complete_dfa.initial_state,
            final_states=complete_dfa.final_states,
            allow_partial=True,
        )

        self.assertEqual(complete_dfa.states, complete_dfa.to_complete().states)
        self.assertEqual(
            len(self.partial_dfa.states), len(test_dfa.to_partial().states)
        )

        self.assertTrue(
            set(test_dfa.to_partial(minify=False).states).issubset(complete_dfa.states)
        )

    def test_equivalence_complete(self) -> None:
        frag = DFA(
            states={0, 1, 2, 3, 4},
            input_symbols={"0", "1"},
            transitions={
                0: {"1": 0, "0": 0},
                1: {"1": 0, "0": 3},
                3: {"1": 1, "0": 4},
                2: {"1": 0, "0": 4},
                4: {"1": 2, "0": 3},
            },
            initial_state=3,
            final_states={1, 4},
        )

        self.assertEqual(frag, frag.minify())
        self.assertEqual(frag, frag.to_partial())

    def test_equivalence_minify(self) -> None:
        minimal_dfa = self.no_consecutive_11_dfa.minify()
        self.assertEqual(self.no_consecutive_11_dfa, minimal_dfa)

        other_dfa = DFA(
            states={0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
            input_symbols={"a", "c", "b"},
            transitions={
                0: {"b": 1, "a": 2},
                1: {"b": 3, "a": 4, "c": 5},
                2: {"b": 6, "c": 5, "a": 4},
                3: {"b": 7, "c": 8},
                4: {"b": 9, "c": 10},
                5: {"b": 9, "c": 10},
                6: {"b": 9, "c": 10},
                7: {"b": 7, "c": 8},
                8: {"b": 9, "c": 10},
                9: {"c": 10, "b": 9},
                10: {"c": 10, "b": 9},
            },
            initial_state=0,
            final_states={2, 7, 8, 9, 10},
            allow_partial=True,
        )

        self.assertEqual(other_dfa, other_dfa.minify())

    def test_equivalence_two_non_minimal(self) -> None:
        other_dfa = DFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q3", "1": "q2"},
                "q3": {"0": "q3", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        self.assertEqual(self.no_consecutive_11_dfa, other_dfa)

    def test_complement_partial(self) -> None:
        complement_partial_dfa = self.partial_dfa.complement()
        complement_complete_dfa = self.partial_dfa.to_complete().complement()

        self.assertEqual(complement_complete_dfa, complement_partial_dfa)

    def test_complement(self) -> None:
        complement_dfa = self.no_consecutive_11_dfa.complement(
            retain_names=True, minify=False
        )
        self.assertEqual(complement_dfa.states, self.no_consecutive_11_dfa.states)
        self.assertEqual(
            complement_dfa.input_symbols, self.no_consecutive_11_dfa.input_symbols
        )
        self.assertEqual(
            complement_dfa.transitions, self.no_consecutive_11_dfa.transitions
        )
        self.assertEqual(
            complement_dfa.initial_state, self.no_consecutive_11_dfa.initial_state
        )
        self.assertEqual(complement_dfa.final_states, {"p2"})

    def test_union(self) -> None:
        dfa1 = self.at_least_four_ones
        dfa2 = self.no_consecutive_11_dfa
        new_dfa = dfa1.union(dfa2, retain_names=True, minify=False)
        self.assertEqual(
            new_dfa.states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q2", "p2"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q3", "p2"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.transitions,
            {
                ("q0", "p0"): {"0": ("q0", "p0"), "1": ("q1", "p1")},
                ("q1", "p0"): {"0": ("q1", "p0"), "1": ("q2", "p1")},
                ("q1", "p1"): {"0": ("q1", "p0"), "1": ("q2", "p2")},
                ("q2", "p0"): {"0": ("q2", "p0"), "1": ("q3", "p1")},
                ("q2", "p1"): {"0": ("q2", "p0"), "1": ("q3", "p2")},
                ("q2", "p2"): {"0": ("q2", "p2"), "1": ("q3", "p2")},
                ("q3", "p0"): {"0": ("q3", "p0"), "1": ("q4", "p1")},
                ("q3", "p1"): {"0": ("q3", "p0"), "1": ("q4", "p2")},
                ("q3", "p2"): {"0": ("q3", "p2"), "1": ("q4", "p2")},
                ("q4", "p0"): {"0": ("q4", "p0"), "1": ("q4", "p1")},
                ("q4", "p1"): {"0": ("q4", "p0"), "1": ("q4", "p2")},
                ("q4", "p2"): {"0": ("q4", "p2"), "1": ("q4", "p2")},
            },
        )
        self.assertEqual(new_dfa.initial_state, ("q0", "p0"))
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q4", "p0"),
                ("q4", "p1"),
                ("q4", "p2"),
            },
        )

        self.assertEqual(dfa1.union(dfa2, retain_names=False, minify=False), new_dfa)

    def test_intersection(self) -> None:
        dfa1 = self.at_least_four_ones
        dfa2 = self.no_consecutive_11_dfa
        new_dfa = dfa1.intersection(dfa2, retain_names=True, minify=False)
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q4", "p0"),
                ("q4", "p1"),
            },
        )
        self.assertEqual(
            dfa1.intersection(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_difference(self) -> None:
        dfa1 = self.at_least_four_ones
        dfa2 = self.no_consecutive_11_dfa
        new_dfa = dfa1.difference(dfa2, retain_names=True, minify=False)
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(new_dfa.final_states, {("q4", "p2")})
        self.assertEqual(
            dfa1.difference(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_symmetric_difference(self) -> None:
        dfa1 = self.at_least_four_ones
        dfa2 = self.no_consecutive_11_dfa
        new_dfa = dfa1.symmetric_difference(dfa2, retain_names=True, minify=False)
        self.assertEqual(new_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            new_dfa.final_states,
            {
                ("q0", "p0"),
                ("q1", "p0"),
                ("q1", "p1"),
                ("q2", "p0"),
                ("q2", "p1"),
                ("q3", "p0"),
                ("q3", "p1"),
                ("q4", "p2"),
            },
        )
        self.assertEqual(
            dfa1.symmetric_difference(dfa2, retain_names=False, minify=False), new_dfa
        )

    def test_issubset(self) -> None:
        self.assertTrue(self.zero_or_one_1_dfa < self.no_consecutive_11_dfa)
        self.assertTrue(self.zero_or_one_1_dfa <= self.no_consecutive_11_dfa)
        self.assertFalse(self.no_consecutive_11_dfa < self.zero_or_one_1_dfa)
        self.assertFalse(self.no_consecutive_11_dfa <= self.zero_or_one_1_dfa)

        single_string_dfa = DFA.from_finite_language(
            {"0", "1"}, {"101"}, as_partial=True
        )

        self.assertFalse(self.partial_dfa < self.zero_or_one_1_dfa)
        self.assertFalse(self.partial_dfa <= self.zero_or_one_1_dfa)

        self.assertTrue(single_string_dfa < self.no_consecutive_11_dfa)
        self.assertTrue(single_string_dfa <= self.no_consecutive_11_dfa)

    def test_issuperset(self) -> None:
        self.assertFalse(self.zero_or_one_1_dfa > self.no_consecutive_11_dfa)
        self.assertFalse(self.zero_or_one_1_dfa >= self.no_consecutive_11_dfa)

        self.assertTrue(self.no_consecutive_11_dfa > self.zero_or_one_1_dfa)
        self.assertTrue(self.no_consecutive_11_dfa >= self.zero_or_one_1_dfa)

        single_string_dfa = DFA.from_finite_language(
            {"0", "1"}, {"101"}, as_partial=True
        )

        self.assertFalse(self.zero_or_one_1_dfa > self.partial_dfa)
        self.assertFalse(self.zero_or_one_1_dfa >= self.partial_dfa)

        self.assertTrue(self.no_consecutive_11_dfa > single_string_dfa)
        self.assertTrue(self.no_consecutive_11_dfa >= single_string_dfa)

    def test_symbol_mismatch(self) -> None:
        zero_or_one_b_dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": "q0", "b": "q1"},
                "q1": {"a": "q1", "b": "q2"},
                "q2": {"a": "q2", "b": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.issubset(self.no_consecutive_11_dfa)

        with self.assertRaises(exceptions.SymbolMismatchError):
            zero_or_one_b_dfa.difference(self.no_consecutive_11_dfa)

    def test_isdisjoint(self) -> None:
        input_symbols = {"0", "1"}
        at_least_three_1 = DFA.from_subsequence(input_symbols, "111")
        at_least_one_1 = DFA.from_subsequence(input_symbols, "1")

        self.assertTrue(at_least_three_1.isdisjoint(self.zero_or_one_1_dfa))
        self.assertTrue(self.zero_or_one_1_dfa.isdisjoint(at_least_three_1))

        self.assertFalse(at_least_three_1.isdisjoint(at_least_one_1))
        self.assertFalse(self.zero_or_one_1_dfa.isdisjoint(at_least_one_1))

        self.assertTrue(self.zero_or_one_1_dfa.isdisjoint(self.partial_dfa))
        self.assertTrue(self.partial_dfa.isdisjoint(self.zero_or_one_1_dfa))

        self.assertFalse(at_least_three_1.isdisjoint(self.partial_dfa))
        self.assertFalse(self.partial_dfa.isdisjoint(at_least_three_1))

    @parameterized.expand(
        get_permutation_tuples(
            DFA.from_substring(set("01"), "1111"),
            DfaTestCase.partial_dfa,
            DfaTestCase.no_consecutive_11_dfa,
            DfaTestCase.at_least_four_ones,
            DfaTestCase.zero_or_one_1_dfa,
            DfaTestCase.no_reachable_final_dfa,
        )
    )
    def test_set_laws(self, dfa1: DFA, dfa2: DFA) -> None:
        input_symbols = {"0", "1"}

        dfa1 = dfa1.to_complete()
        dfa2 = dfa2.to_partial()

        self.assertNotEqual(dfa1, dfa2)

        universal = DFA.universal_language(input_symbols)
        empty = DFA.empty_language(input_symbols)
        self.assertEqual(~(dfa1 | dfa2), ~dfa1 & ~dfa2)
        self.assertEqual(~(dfa1 & dfa2), ~dfa1 | ~dfa2)
        self.assertEqual(dfa1 | ~dfa1, universal)
        self.assertEqual(dfa1 & ~dfa1, empty)
        self.assertEqual(~universal, empty)
        self.assertEqual(~empty, universal)
        self.assertEqual(dfa1, ~(~dfa1))
        self.assertEqual(dfa1 - dfa2, dfa1 & ~dfa2)
        self.assertEqual(~(dfa1 - dfa2), ~dfa1 | dfa2)
        self.assertEqual(~(dfa1 - dfa2), ~dfa1 | (dfa2 & dfa1))
        self.assertEqual(~dfa1 - ~dfa2, dfa2 - dfa1)
        self.assertEqual(dfa1 ^ dfa2, (dfa1 - dfa2) | (dfa2 - dfa1))
        self.assertEqual(dfa1 ^ dfa2, (dfa1 | dfa2) - (dfa1 & dfa2))
        self.assertEqual(dfa1 | dfa2, dfa2 | dfa1)
        self.assertEqual(dfa1 & dfa2, dfa2 & dfa1)
        self.assertEqual(dfa1 ^ dfa2, dfa2 ^ dfa1)


__all__ = ["TestDfaEquivalence"]
