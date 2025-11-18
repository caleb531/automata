"""Length and counting related DFA helpers."""

from parameterized import parameterized  # type: ignore

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from tests.test_dfa.base import DFATestCase


class TestDFALengthConstraints(DFATestCase):
    """Validate language length constraints, counting, and caches."""

    def test_count_words_of_length(self) -> None:
        """Test that language that avoids the pattern '11' is counted by fibonacci
        numbers"""
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

        fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i, fib in enumerate(fibonacci):
            self.assertEqual(dfa.count_words_of_length(i), fib)

    def test_words_of_length(self) -> None:
        """Test that all words generated are accepted and that count matches"""
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

        fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i, fib in enumerate(fibonacci):
            count = 0
            for word in dfa.words_of_length(i):
                count += 1
                self.assertIn(word, dfa)
            self.assertEqual(count, fib)

    @parameterized.expand((True, False))
    def test_of_length(self, as_partial: bool) -> None:
        binary = {"0", "1"}
        dfa1 = DFA.of_length(binary)
        self.assertFalse(dfa1.isfinite())
        self.assertEqual(len(dfa1.states), len(dfa1.minify().states))
        self.assertEqual(dfa1, DFA.universal_language(binary))
        self.assertEqual(dfa1.minimum_word_length(), 0)
        self.assertIsNone(dfa1.maximum_word_length())

        dfa2 = DFA.of_length(binary, min_length=5)
        self.assertFalse(dfa2.isfinite())
        self.assertEqual(len(dfa2.states), len(dfa2.minify().states))
        generator = iter(dfa2)
        for word in generator:
            if len(word) > 8:
                break
            self.assertGreaterEqual(len(word), 5)
        self.assertEqual(dfa2.minimum_word_length(), 5)
        self.assertIsNone(dfa2.maximum_word_length())

        dfa3 = DFA.of_length(binary, min_length=0, max_length=4)
        self.assertTrue(dfa3.isfinite())
        self.assertEqual(len(dfa3.states), len(dfa3.minify().states))
        expected = [
            "",
            "0",
            "1",
            "00",
            "01",
            "10",
            "11",
            "000",
            "001",
            "010",
            "011",
            "100",
            "101",
            "110",
            "111",
            "0000",
            "0001",
            "0010",
            "0011",
            "0100",
            "0101",
            "0110",
            "0111",
            "1000",
            "1001",
            "1010",
            "1011",
            "1100",
            "1101",
            "1110",
            "1111",
        ]
        self.assertListEqual(list(dfa3), expected)
        self.assertEqual(
            dfa3, DFA.from_finite_language(binary, set(expected), as_partial)
        )
        self.assertEqual(dfa1, dfa2.union(dfa3))
        self.assertEqual(dfa3.minimum_word_length(), 0)
        self.assertEqual(dfa3.maximum_word_length(), 4)

        dfa4 = DFA.of_length(binary, min_length=4, max_length=8)
        self.assertTrue(dfa4.isfinite())
        self.assertEqual(len(dfa4.states), len(dfa4.minify().states))
        expected_counts = [
            0,
            0,
            0,
            0,
            2**4,
            2**5,
            2**6,
            2**7,
            2**8,
            0,
            0,
            0,
            0,
        ]
        actual_counts = [
            dfa4.count_words_of_length(i) for i, _ in enumerate(expected_counts)
        ]
        self.assertListEqual(actual_counts, expected_counts)
        self.assertEqual(dfa4.minimum_word_length(), 4)
        self.assertEqual(dfa4.maximum_word_length(), 8)

        dfa5 = DFA.of_length(binary, min_length=2, max_length=2, symbols_to_count={"1"})
        dfa6 = DFA(
            states={0, 1, 2, 3},
            input_symbols=binary,
            transitions={
                0: {"1": 1, "0": 0},
                1: {"1": 2, "0": 1},
                2: {"1": 3, "0": 2},
                3: {"1": 3, "0": 3},
            },
            initial_state=0,
            final_states={2},
        )
        self.assertEqual(dfa5, dfa6)

        dfa7 = DFA.of_length(binary, symbols_to_count={"1"})
        dfa8 = DFA.of_length(binary, symbols_to_count={"0"})
        self.assertEqual(dfa7.union(dfa8), DFA.universal_language(binary))

    def test_count_mod(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            DFA.count_mod(binary, 0)

        no_symbols = DFA.count_mod(binary, 4, symbols_to_count=set())
        self.assertEqual(no_symbols, DFA.universal_language(binary))

        no_symbols_empty = DFA.count_mod(
            binary, 4, remainders={1, 2, 3}, symbols_to_count=set()
        )
        self.assertEqual(no_symbols_empty, DFA.empty_language(binary))

        even = DFA.count_mod(binary, 2)
        for word in even:
            if len(word) >= 8:
                break
            self.assertEqual(len(word) % 2, 0)

        odd = DFA.count_mod(binary, 2, remainders={1})
        for word in odd:
            if len(word) >= 8:
                break
            self.assertEqual(len(word) % 2, 1)

        even_1 = DFA.count_mod(binary, 2, symbols_to_count={"1"})
        for word in even_1:
            if len(word) >= 8:
                break
            self.assertEqual(word.count("1") % 2, 0)

        odd_0 = DFA.count_mod(binary, 2, remainders={1}, symbols_to_count={"0"})
        for word in odd_0:
            if len(word) >= 8:
                break
            self.assertEqual(word.count("0") % 2, 1)

        self.assertEqual(
            DFA.count_mod(binary, 4, remainders={0, 2}), DFA.count_mod(binary, 2)
        )

    def test_nth_from_start(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            DFA.nth_from_start(binary, "0", 0)

        with self.assertRaises(exceptions.InvalidSymbolError):
            DFA.nth_from_start(binary, "2", 1)

        dfa = DFA.nth_from_start({"0"}, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertListEqual(list(~dfa), [""])
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_start(binary, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertIn("00", dfa)
        self.assertIn("01", dfa)
        self.assertNotIn("10", dfa)
        self.assertNotIn("11", dfa)
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_start(binary, "0", 2)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertIn("00", dfa)
        self.assertNotIn("01", dfa)
        self.assertIn("10", dfa)
        self.assertNotIn("11", dfa)
        self.assertEqual(dfa.minimum_word_length(), 2)

        dfa = DFA.nth_from_start(binary, "0", 3)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 3)

        dfa = DFA.nth_from_start(binary, "1", 4)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 4)

    def test_nth_from_end(self) -> None:
        binary = {"0", "1"}
        with self.assertRaises(ValueError):
            DFA.nth_from_end(binary, "0", 0)

        with self.assertRaises(exceptions.InvalidSymbolError):
            DFA.nth_from_end(binary, "2", 1)

        dfa = DFA.nth_from_end({"0"}, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_end(binary, "0", 1)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 1)

        dfa = DFA.nth_from_end(binary, "0", 2)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 2)

        dfa = DFA.nth_from_end(binary, "0", 3)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 3)

        dfa = DFA.nth_from_end(binary, "1", 4)
        self.assertFalse(dfa.isfinite())
        self.assertEqual(len(dfa.states), len(dfa.minify().states))
        self.assertEqual(dfa.minimum_word_length(), 4)

    @parameterized.expand((True, False))
    def test_reset_word_cache(self, as_partial: bool) -> None:
        max_len = 4
        dfa = DFA.of_length({"0", "1"}, min_length=0, max_length=max_len)

        if as_partial:
            dfa = dfa.to_partial()

        self.assertEqual(len(dfa._word_cache), 0)
        self.assertEqual(len(dfa._count_cache), 0)

        self.assertGreater(dfa.cardinality(), 0)
        self.assertGreater(len(dfa._count_cache), 0)

        self.assertGreater(len(list(dfa.words_of_length(max_len))), 0)
        self.assertGreater(len(dfa._word_cache), 0)

        dfa.clear_cache()
        self.assertEqual(len(dfa._word_cache), 0)
        self.assertEqual(len(dfa._count_cache), 0)
