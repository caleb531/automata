"""Algebraic operations on NFAs."""

import string

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from tests.test_nfa.base import NfaTestCase


class TestNfaOperations(NfaTestCase):
    """Exercise concatenation, closure, and set-like operations."""

    def test_operations_other_type(self) -> None:
        nfa = NFA(
            states={"q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q1": {"0": {"q1"}, "1": {"q1", "q2"}},
                "q2": {"": {"q2"}, "0": {"q2"}},
                "q3": {"1": {"q4"}},
                "q4": {"0": {"q4"}, "1": {"q4"}},
            },
            initial_state="q1",
            final_states={"q2", "q4"},
        )
        other = 42
        with self.assertRaises(TypeError):
            nfa + other  # type: ignore

    def test_concatenate(self) -> None:
        nfa_a = NFA(
            states={"q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q1": {"0": {"q1"}, "1": {"q1", "q2"}},
                "q2": {"": {"q2"}, "0": {"q2"}},
                "q3": {"1": {"q4"}},
                "q4": {"0": {"q4"}, "1": {"q4"}},
            },
            initial_state="q1",
            final_states={"q2", "q4"},
        )

        nfa_b = NFA(
            states={"r1", "r2", "r3"},
            input_symbols={"0", "1"},
            transitions={
                "r1": {"": {"r3"}, "1": {"r2"}},
                "r2": {"0": {"r2", "r3"}, "1": {"r3"}},
                "r3": {"0": {"r1"}},
            },
            initial_state="r1",
            final_states={"r1"},
        )

        concat_nfa = nfa_a + nfa_b

        self.assertFalse(concat_nfa.accepts_input(""))
        self.assertFalse(concat_nfa.accepts_input("0"))
        self.assertTrue(concat_nfa.accepts_input("1"))
        self.assertFalse(concat_nfa.accepts_input("00"))
        self.assertTrue(concat_nfa.accepts_input("01"))
        self.assertTrue(concat_nfa.accepts_input("10"))
        self.assertTrue(concat_nfa.accepts_input("11"))
        self.assertTrue(concat_nfa.accepts_input("101"))
        self.assertTrue(concat_nfa.accepts_input("101100"))
        self.assertTrue(concat_nfa.accepts_input("1010"))

    def test_kleene_star(self) -> None:
        nfa = NFA(
            states={0, 1, 2, 3, 4, 6, 10},
            input_symbols={"a", "b"},
            transitions={
                0: {"a": {1, 3}},
                1: {"b": {2}},
                2: {},
                3: {"a": {4}},
                4: {"": {6}},
                6: {},
            },
            initial_state=0,
            final_states={2, 4, 6, 10},
        )
        kleene_nfa = nfa.kleene_star()
        self.assertTrue(kleene_nfa.accepts_input(""))
        self.assertFalse(kleene_nfa.accepts_input("a"))
        self.assertFalse(kleene_nfa.accepts_input("b"))
        self.assertTrue(kleene_nfa.accepts_input("aa"))
        self.assertTrue(kleene_nfa.accepts_input("ab"))
        self.assertFalse(kleene_nfa.accepts_input("ba"))
        self.assertFalse(kleene_nfa.accepts_input("bb"))
        self.assertFalse(kleene_nfa.accepts_input("aaa"))
        self.assertFalse(kleene_nfa.accepts_input("aba"))
        self.assertTrue(kleene_nfa.accepts_input("abaa"))
        self.assertFalse(kleene_nfa.accepts_input("abba"))
        self.assertFalse(kleene_nfa.accepts_input("aaabababaaaaa"))
        self.assertTrue(kleene_nfa.accepts_input("aaabababaaaaab"))
        self.assertFalse(kleene_nfa.accepts_input("aaabababaaaaba"))

    def test_reverse(self) -> None:
        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={"a", "b"},
            transitions={
                0: {"a": {1}},
                1: {"a": {2}, "b": {1, 2}},
                2: {},
                3: {"a": {2}, "b": {2}},
            },
            initial_state=0,
            final_states={2},
        )

        reverse_nfa = nfa.reverse()
        self.assertFalse(reverse_nfa.accepts_input("a"))
        self.assertFalse(reverse_nfa.accepts_input("ab"))
        self.assertTrue(reverse_nfa.accepts_input("ba"))
        self.assertTrue(reverse_nfa.accepts_input("bba"))
        self.assertTrue(reverse_nfa.accepts_input("bbba"))

    def test_option(self) -> None:
        nfa1 = NFA.from_regex("a*b")
        nfa1 = nfa1.option()
        self.assertTrue(nfa1.accepts_input("aab"))
        self.assertTrue(
            nfa1.initial_state in nfa1.final_states
            and nfa1.initial_state
            not in sum(
                [
                    list(nfa1.transitions[state].values())
                    for state in nfa1.transitions.keys()
                ],
                [],
            )
        )

    def test_union(self) -> None:
        input_symbols = {"a", "b"}
        nfa1 = NFA.from_regex("ab*", input_symbols=input_symbols)
        nfa2 = NFA.from_regex("ba*", input_symbols=input_symbols)

        nfa3 = nfa1.union(nfa2)

        nfa4 = NFA(
            states={0, 1, 2, 3, 4},
            input_symbols=input_symbols,
            transitions={
                0: {"": {1, 3}},
                2: {"b": {2}},
                1: {"a": {2}},
                3: {"b": {4}},
                4: {"a": {4}},
            },
            final_states={2, 4},
            initial_state=0,
        )

        self.assertEqual(nfa3, nfa4)

        nfa5 = nfa1 | nfa2
        self.assertEqual(nfa5, nfa4)

        nfa6 = NFA.from_regex("aa*")
        nfa7 = NFA.from_regex("a*")
        nfa8 = nfa6.union(nfa7)
        nfa9 = nfa7.union(nfa6)
        self.assertEqual(nfa8, nfa7)
        self.assertEqual(nfa9, nfa7)

        with self.assertRaises(TypeError):
            self.nfa | self.dfa  # type: ignore

    def test_intersection(self) -> None:
        nfa1 = NFA.from_regex("aaaa*")
        nfa2 = NFA.from_regex("(a)|(aa)|(aaa)")

        nfa3 = nfa1.intersection(nfa2)

        nfa4 = NFA.from_regex("aaa")
        self.assertEqual(nfa3, nfa4)

        nfa5 = nfa1 & nfa2
        self.assertEqual(nfa5, nfa4)

        nfa6 = NFA.from_regex("aa*")
        nfa7 = NFA.from_regex("a*")
        nfa8 = nfa6.intersection(nfa7)
        nfa9 = nfa7.intersection(nfa6)
        self.assertEqual(nfa8, nfa6)
        self.assertEqual(nfa9, nfa6)

        with self.assertRaises(TypeError):
            self.nfa & self.dfa  # type: ignore

    def test_nfa_shuffle_product(self) -> None:
        input_symbols = {"a", "b"}

        nfa1 = NFA.from_dfa(DFA.from_finite_language(input_symbols, {"aba"}))
        nfa2 = NFA.from_dfa(DFA.from_finite_language(input_symbols, {"bab"}))

        nfa3 = NFA.from_dfa(
            DFA.from_finite_language(
                input_symbols,
                {
                    "abbaab",
                    "baabab",
                    "ababab",
                    "babaab",
                    "abbaba",
                    "baabba",
                    "ababba",
                    "bababa",
                },
            )
        )

        self.assertEqual(nfa1.shuffle_product(nfa2), nfa3)

        nfa4 = NFA.from_regex("aa", input_symbols=input_symbols)
        nfa5 = NFA.from_regex("b*", input_symbols=input_symbols)

        nfa6 = NFA.from_dfa(
            DFA.of_length(
                input_symbols, min_length=2, max_length=2, symbols_to_count={"a"}
            )
        )

        self.assertEqual(nfa4.shuffle_product(nfa5), nfa6)

        nfa7 = NFA.from_regex("a?a?a?", input_symbols=input_symbols)
        nfa8 = NFA.from_dfa(
            DFA.of_length(input_symbols, max_length=3, symbols_to_count={"a"})
        )

        self.assertEqual(nfa5.shuffle_product(nfa7), nfa8)

        with self.assertRaises(TypeError):
            self.nfa.shuffle_product(self.dfa)  # type: ignore

    def test_nfa_shuffle_product_set_laws(self) -> None:
        alphabet = {"a", "b"}
        nfa1 = NFA.from_regex("a*b*", input_symbols=alphabet)
        nfa2 = NFA.from_regex("b*a*", input_symbols=alphabet)
        nfa3 = NFA.from_regex("ab*a", input_symbols=alphabet)

        self.assertEqual(nfa1.shuffle_product(nfa2), nfa2.shuffle_product(nfa1))
        self.assertEqual(
            nfa1.shuffle_product(nfa2.shuffle_product(nfa3)),
            nfa1.shuffle_product(nfa2).shuffle_product(nfa3),
        )
        self.assertEqual(
            nfa1.shuffle_product(nfa2.union(nfa3)),
            nfa1.shuffle_product(nfa2).union(nfa1.shuffle_product(nfa3)),
        )

    def test_right_quotient(self) -> None:
        alphabet = set(string.ascii_lowercase)

        nfa1 = NFA.from_dfa(
            DFA.from_finite_language(alphabet, {"hooray", "sunray", "defray", "ray"})
        )
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {"ray"}))

        quotient_dfa_1 = DFA.from_nfa(nfa1.right_quotient(nfa2))
        reference_dfa_1 = DFA.from_finite_language(alphabet, {"hoo", "sun", "def", ""})

        self.assertEqual(quotient_dfa_1, reference_dfa_1)

        nfa3 = NFA.from_dfa(
            DFA.from_finite_language({"a", "b"}, {"", "a", "ab", "aba", "abab", "abb"})
        )
        nfa4 = NFA.from_dfa(
            DFA.from_finite_language({"a", "b"}, {"b", "bb", "bbb", "bbbb"})
        )

        quotient_dfa_2 = DFA.from_nfa(nfa3.right_quotient(nfa4))
        reference_dfa_2 = DFA.from_finite_language({"a", "b"}, {"a", "aba", "ab"})

        self.assertEqual(quotient_dfa_2, reference_dfa_2)

        nfa_5 = NFA.from_regex("bba*baa*")
        nfa_6 = NFA.from_regex("ab*")

        quotient_nfa_3 = nfa_5.right_quotient(nfa_6)
        reference_nfa_3 = NFA.from_regex("bba*ba*")

        self.assertEqual(quotient_nfa_3, reference_nfa_3)

        nfa_7 = NFA.from_regex("a*baa*")
        nfa_8 = NFA.from_regex("ab*")

        quotient_nfa_4 = nfa_7.right_quotient(nfa_8)
        reference_nfa_4 = NFA.from_regex("a*ba*")

        self.assertEqual(quotient_nfa_4, reference_nfa_4)

        nfa_9 = NFA.from_regex("a+bc+")
        nfa_10 = NFA.from_regex("c+")

        quotient_nfa_5 = nfa_9.right_quotient(nfa_10)
        reference_nfa_5 = NFA.from_regex("a+bc*")

        self.assertEqual(quotient_nfa_5, reference_nfa_5)

        with self.assertRaises(TypeError):
            self.nfa.right_quotient(self.dfa)  # type: ignore

    def test_left_quotient(self) -> None:
        alphabet = set(string.ascii_lowercase)

        nfa1 = NFA.from_dfa(
            DFA.from_finite_language(alphabet, {"match", "matter", "mat", "matzoth"})
        )
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {"mat"}))

        quotient_dfa_1 = DFA.from_nfa(nfa1.left_quotient(nfa2))
        reference_dfa_1 = DFA.from_finite_language(alphabet, {"ch", "ter", "", "zoth"})

        self.assertEqual(quotient_dfa_1, reference_dfa_1)

        nfa3 = NFA.from_dfa(
            DFA.from_finite_language({"0", "1"}, {"10", "100", "1010", "101110"})
        )
        nfa4 = NFA.from_dfa(DFA.from_finite_language({"0", "1"}, {"10"}))

        quotient_dfa_2 = DFA.from_nfa(nfa3.left_quotient(nfa4))
        reference_dfa_2 = DFA.from_finite_language({"0", "1"}, {"", "0", "10", "1110"})

        self.assertEqual(quotient_dfa_2, reference_dfa_2)

        nfa_5 = NFA.from_regex("0*1")
        nfa_6 = NFA.from_regex("01*")

        quotient_nfa_3 = nfa_5.left_quotient(nfa_6)
        reference_nfa_3 = NFA.from_regex("0*1") | NFA.from_regex("")

        self.assertEqual(quotient_nfa_3, reference_nfa_3)

        nfa_7 = NFA.from_regex("ab*aa*")
        nfa_8 = NFA.from_regex("ab*")

        quotient_nfa_4 = nfa_7.left_quotient(nfa_8)
        reference_nfa_4 = NFA.from_regex("b*aa*")

        self.assertEqual(quotient_nfa_4, reference_nfa_4)

        with self.assertRaises(TypeError):
            self.nfa.left_quotient(self.dfa)  # type: ignore

    def test_quotient_properties(self) -> None:
        nfa1 = NFA.from_regex("(ab*aa*)|(baa+)")
        nfa2 = NFA.from_regex("(aa*b*a)|(b+aaba)")

        nfa1_reversed = nfa1.reverse()
        nfa2_reversed = nfa2.reverse()

        self.assertEqual(
            nfa1.right_quotient(nfa2).reverse(),
            nfa1_reversed.left_quotient(nfa2_reversed),
        )
        self.assertEqual(
            nfa1.left_quotient(nfa2).reverse(),
            nfa1_reversed.right_quotient(nfa2_reversed),
        )

        def is_subset_nfa(nfa_a: NFA, nfa_b: NFA) -> bool:
            return (nfa_a | nfa_b) == nfa_b

        self.assertTrue(
            is_subset_nfa(
                nfa1.left_quotient(nfa2) + nfa2, (nfa1 + nfa2).left_quotient(nfa2)
            )
        )
        self.assertTrue(
            is_subset_nfa(
                nfa2 + nfa1.right_quotient(nfa2), (nfa2 + nfa1).right_quotient(nfa2)
            )
        )


__all__ = ["TestNfaOperations"]
