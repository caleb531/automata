"""Enumeration and ordering behaviors for DFAs."""

from parameterized import parameterized  # type: ignore

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from tests.test_dfa.base import DFATestCase


class TestDFAEnumeration(DFATestCase):
    """Cover iteration, length, and lexical ordering helpers."""

    @parameterized.expand((True, False))
    def test_iter_finite(self, as_partial: bool) -> None:
        """Test that DFA for finite language generates all words"""
        language = {
            "aa",
            "aaa",
            "aaba",
            "aabbb",
            "abaa",
            "ababb",
            "abbab",
            "baa",
            "babb",
            "bbaa",
            "bbabb",
            "bbbab",
        }
        dfa = DFA.from_finite_language({"a", "b"}, language, as_partial=as_partial)
        generated_set = {word for word in dfa}
        self.assertEqual(generated_set, language)

    def test_iter_infinite(self) -> None:
        """Test that language that avoids the pattern '11' generates the correct
        values in correct order"""
        dfa = DFA(
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

        generator = iter(dfa)
        expected = [
            "",
            "0",
            "1",
            "00",
            "01",
            "10",
            "000",
            "001",
            "010",
            "100",
            "101",
            "0000",
            "0001",
            "0010",
            "0100",
            "0101",
            "1000",
            "1001",
            "1010",
        ]
        generated_list = [next(generator) for _ in expected]
        self.assertEqual(generated_list, expected)

    @parameterized.expand((True, False))
    def test_len_finite(self, as_partial: bool) -> None:
        input_symbols = {"a", "b"}
        dfa = DFA.from_finite_language(input_symbols, set(), as_partial)
        self.assertEqual(len(dfa), 0)
        dfa = DFA.from_finite_language(input_symbols, {""}, as_partial)
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(input_symbols, {"a"}, as_partial)
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(input_symbols, {"ababababab"}, as_partial)
        self.assertEqual(len(dfa), 1)
        dfa = DFA.from_finite_language(
            input_symbols, {"a" * i for i in range(5)}, as_partial
        )
        self.assertEqual(len(dfa), 5)
        dfa = DFA.from_finite_language(
            input_symbols,
            {"a" * i + "b" * j for i in range(5) for j in range(5)},
            as_partial,
        )
        self.assertEqual(len(dfa), 25)

    def test_len_infinite(self) -> None:
        dfa = DFA(
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
        with self.assertRaises(exceptions.InfiniteLanguageException):
            len(dfa)
        with self.assertRaises(exceptions.InfiniteLanguageException):
            len(~dfa)

    def test_random_word(self) -> None:
        """Test random generation of words, the generation should be uniformly random"""
        binary = {"0", "1"}
        dfa = DFA.from_prefix(binary, "00")
        with self.assertRaises(ValueError):
            dfa.random_word(1)

        for _ in range(10):
            self.assertEqual(dfa.random_word(2), "00")

        for _ in range(10):
            self.assertIn(dfa.random_word(10), dfa)

        for _ in range(10):
            self.assertIn(dfa.random_word(100), dfa)

    @parameterized.expand((True, False))
    def test_predecessor(self, as_partial: bool) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language, as_partial)
        expected = sorted(language, reverse=True)
        actual = list(dfa.predecessors("11111111111111111111111111111111"))
        self.assertListEqual(actual, expected)
        expected = sorted({"", "0", "00", "000", "010"}, reverse=True)
        actual = list(dfa.predecessors("010", strict=False))

        self.assertEqual(dfa.predecessor("000"), "00")
        self.assertEqual(dfa.predecessor("000", max_length=1), "0")
        self.assertIsNone(dfa.predecessor("0", min_length=2))
        self.assertEqual(dfa.predecessor("0000", min_length=2, max_length=3), "000")
        self.assertEqual(dfa.predecessor("0100"), "010")
        self.assertEqual(dfa.predecessor("1"), "010101111111101011010100")
        self.assertEqual(
            dfa.predecessor("0111111110101011"), "010101111111101011010100"
        )
        self.assertIsNone(dfa.predecessor(""))

        infinite_dfa = DFA.from_nfa(NFA.from_regex("0*1*"))
        with self.assertRaises(exceptions.InfiniteLanguageException):
            infinite_dfa.predecessor("000")
        with self.assertRaises(exceptions.InfiniteLanguageException):
            list(infinite_dfa.predecessors("000"))

    @parameterized.expand((True, False))
    def test_successor(self, as_partial: bool) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language, as_partial)
        expected = sorted(language)
        actual = list(dfa.successors("", strict=False))
        self.assertListEqual(actual, expected)

        self.assertEqual(dfa.successor("000"), "010")
        self.assertEqual(dfa.successor("0100"), "010101111111101011010100")
        self.assertIsNone(dfa.successor("110"))
        self.assertIsNone(dfa.successor("111111110101011"))

        self.assertEqual(dfa.successor("", min_length=3), "000")
        self.assertEqual(dfa.successor("", min_length=4), "010101111111101011010100")
        self.assertEqual(dfa.successor("010", max_length=6), "100")

        infinite_dfa = DFA.from_nfa(NFA.from_regex("0*1*"))
        self.assertEqual(infinite_dfa.successor(""), "0")
        self.assertEqual(infinite_dfa.successor("0"), "00")
        self.assertEqual(infinite_dfa.successor("00"), "000")
        self.assertEqual(infinite_dfa.successor("0001"), "00011")
        self.assertEqual(infinite_dfa.successor("00011"), "000111")
        self.assertEqual(infinite_dfa.successor("0000000011111"), "00000000111111")
        self.assertEqual(infinite_dfa.successor("1"), "11")
        self.assertEqual(infinite_dfa.successor(100 * "0"), 101 * "0")
        self.assertEqual(infinite_dfa.successor(100 * "1"), 101 * "1")
        self.assertEqual(infinite_dfa.successor("", min_length=5), "00000")
        self.assertEqual(infinite_dfa.successor("000", min_length=5), "00000")
        self.assertEqual(infinite_dfa.successor("1", min_length=5), "11111")
        self.assertIsNone(infinite_dfa.successor("1111", max_length=4))

    @parameterized.expand((True, False))
    def test_successor_and_predecessor(self, as_partial: bool) -> None:
        binary = {"0", "1"}
        language = {
            "",
            "0",
            "00",
            "000",
            "010",
            "100",
            "110",
            "010101111111101011010100",
        }
        dfa = DFA.from_finite_language(binary, language, as_partial)
        for word in language:
            self.assertEqual(dfa.successor(dfa.predecessor(word)), word)  # type: ignore
            self.assertEqual(dfa.predecessor(dfa.successor(word)), word)  # type: ignore

    def test_successor_custom_key(self) -> None:
        input_symbols = {"a", "b", "c", "d"}
        order = {"b": 0, "c": 1, "a": 2, "d": 3}
        expected = [
            "",
            "b",
            "ba",
            "bab",
            "bad",
            "c",
            "cd",
            "cda",
            "a",
            "ab",
            "ac",
            "aa",
            "ad",
            "dddddddddddddddddb",
            "dddddddddddddddddd",
        ]
        language = set(expected)
        dfa = DFA.from_finite_language(input_symbols, language)
        actual = list(dfa.successors(None, key=order.get))
        self.assertListEqual(actual, expected)

    def test_successor_partial(self) -> None:
        binary = {"0", "1"}
        dfa = DFA(
            states={0, 1},
            input_symbols=binary,
            transitions={0: {"0": 1}, 1: {"1": 1}},
            initial_state=0,
            final_states={1},
            allow_partial=True,
        )
        self.assertEqual(dfa.successor(None), "0")
        self.assertEqual(dfa.successor(""), "0")
        self.assertEqual(dfa.successor("0"), "01")
        self.assertEqual(dfa.successor("00"), "01")
        self.assertEqual(dfa.successor("0000101010111"), "01")
        self.assertEqual(dfa.successor("01"), "011")
        self.assertEqual(dfa.successor("01000"), "011")
        self.assertIsNone(dfa.successor("1"))
