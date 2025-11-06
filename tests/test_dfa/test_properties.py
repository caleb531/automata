"""Tests validating core language properties of DFAs."""

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from tests.test_dfa.base import DFATestCase


class TestDFALanguageProperties(DFATestCase):
    """Exercise language emptiness, finiteness, and length bounds."""

    def test_isempty_non_empty(self) -> None:
        dfa = DFA.from_subsequence({"0", "1"}, "111")
        self.assertFalse(dfa.isempty())

    def test_isempty_empty(self) -> None:
        self.assertTrue(self.no_reachable_final_dfa.isempty())

    def test_isfinite_infinite(self) -> None:
        dfa = DFA.from_substring({"0", "1"}, "11").complement(minify=False)
        self.assertFalse(dfa.isfinite())

    def test_isfinite_infinite_case_2(self) -> None:
        dfa = DFA(
            states={"q0", "q1", "q2", "q3", "q4", "q5", "q6"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q2", "1": "q2"},
                "q2": {"0": "q3", "1": "q3"},
                "q3": {"0": "q4", "1": "q4"},
                "q4": {"0": "q5", "1": "q5"},
                "q5": {"0": "q6", "1": "q6"},
                "q6": {"0": "q6", "1": "q6"},
            },
            initial_state="q0",
            final_states={"q0", "q1", "q2", "q3", "q4", "q5", "q6"},
        )
        self.assertFalse(dfa.isfinite())

    def test_isfinite_finite(self) -> None:
        dfa = DFA.of_length({"0", "1"}, min_length=0, max_length=5)
        self.assertTrue(dfa.isfinite())

    def test_isfinite_empty(self) -> None:
        self.assertTrue(self.no_reachable_final_dfa.isfinite())

    def test_isfinite_universe(self) -> None:
        dfa = DFA.universal_language({"0", "1"})
        self.assertFalse(dfa.isfinite())

    def test_minimum_word_length(self) -> None:
        at_least_one_symbol = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q1", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        empty = DFA(
            states={"q0"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q0"}},
            initial_state="q0",
            final_states=set(),
        )

        self.assertEqual(self.at_least_four_ones.minimum_word_length(), 4)
        self.assertEqual(self.no_consecutive_11_dfa.minimum_word_length(), 0)
        self.assertEqual(at_least_one_symbol.minimum_word_length(), 1)
        with self.assertRaises(exceptions.EmptyLanguageException):
            empty.minimum_word_length()

    def test_maximum_word_length(self) -> None:
        at_most_one_symbol = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q2", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        empty = DFA(
            states={"q0"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q0"}},
            initial_state="q0",
            final_states=set(),
        )

        self.assertIsNone(self.at_least_four_ones.maximum_word_length())
        self.assertIsNone(self.no_consecutive_11_dfa.maximum_word_length())
        self.assertEqual(at_most_one_symbol.maximum_word_length(), 1)
        with self.assertRaises(exceptions.EmptyLanguageException):
            empty.maximum_word_length()

    def test_empty_language(self) -> None:
        dfa = DFA.empty_language({"0"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"0", "1"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"a", "b"})
        self.assertTrue(dfa.isempty())

        dfa = DFA.empty_language({"0", "1", "a", "b"})
        self.assertTrue(dfa.isempty())
