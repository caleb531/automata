"""Pattern-based DFA construction helpers."""

from itertools import product

from parameterized import parameterized  # type: ignore

from automata.fa.dfa import DFA
from tests.test_dfa.base import DFATestCase


class TestDFAPatternConstructors(DFATestCase):
    """Exercise prefix, suffix, substring, and subsequence constructors."""

    @parameterized.expand((True, False))
    def test_contains_prefix(self, as_partial: bool) -> None:
        input_symbols = {"a", "n", "o", "b"}

        prefix_dfa = DFA.from_prefix(input_symbols, "nano", as_partial=as_partial)
        self.assertEqual(len(prefix_dfa.states), len(prefix_dfa.minify().states))

        subset_dfa = DFA.from_finite_language(
            input_symbols,
            {"nano", "nanobao", "nanonana", "nanonano", "nanoo"},
            as_partial,
        )
        self.assertTrue(subset_dfa < prefix_dfa)

        self.assertEqual(
            ~prefix_dfa,
            DFA.from_prefix(
                input_symbols, "nano", contains=False, as_partial=as_partial
            ),
        )

        for word in prefix_dfa:
            if len(word) > 8:
                break
            self.assertTrue(word.startswith("nano"))

    @parameterized.expand((True, False))
    def test_contains_suffix(self, as_partial: bool) -> None:
        input_symbols = {"a", "n", "o", "b"}

        suffix_dfa = DFA.from_suffix(input_symbols, "nano")
        self.assertEqual(len(suffix_dfa.states), len(suffix_dfa.minify().states))

        subset_dfa = DFA.from_finite_language(
            input_symbols,
            {"nano", "annnano", "bnano", "anbonano", "nananananananananano"},
            as_partial,
        )
        self.assertTrue(subset_dfa < suffix_dfa)

        self.assertEqual(
            ~suffix_dfa, DFA.from_suffix(input_symbols, "nano", contains=False)
        )

        for word in suffix_dfa:
            if len(word) > 8:
                break
            self.assertTrue(word.endswith("nano"))

    @parameterized.expand((True, False))
    def test_contains_substring(self, as_partial: bool) -> None:
        input_symbols = {"a", "n", "o", "b"}

        equiv_dfa = DFA(
            states={"", "n", "na", "nan", "nano"},
            input_symbols=input_symbols,
            transitions={
                "": {"a": "", "n": "n", "o": "", "b": ""},
                "n": {"a": "na", "n": "n", "o": "", "b": ""},
                "na": {"a": "", "n": "nan", "o": "", "b": ""},
                "nan": {"a": "na", "n": "n", "o": "nano", "b": ""},
                "nano": {"a": "nano", "n": "nano", "o": "nano", "b": "nano"},
            },
            initial_state="",
            final_states={"nano"},
        )

        substring_dfa = DFA.from_substring(input_symbols, "nano")
        self.assertEqual(len(substring_dfa.states), len(substring_dfa.minify().states))

        self.assertEqual(len(substring_dfa.states), len(equiv_dfa.states))
        self.assertEqual(substring_dfa, equiv_dfa)

        subset_dfa = DFA.from_finite_language(
            input_symbols, {"nano", "bananano", "nananano", "naonano"}, as_partial
        )
        self.assertTrue(subset_dfa < substring_dfa)

        self.assertEqual(
            ~substring_dfa, DFA.from_substring(input_symbols, "nano", contains=False)
        )

        for word in substring_dfa:
            if len(word) > 8:
                break
            self.assertIn("nano", word)

    def test_contains_substrings(self) -> None:
        input_symbols = {"a", "n", "o", "b"}
        substring_dfa = DFA.from_substring(input_symbols, "nano")
        substrings_dfa = DFA.from_substrings(input_symbols, {"nano"})

        self.assertEqual(substring_dfa, substrings_dfa)

        substring_dfa = substring_dfa | DFA.from_substring(input_symbols, "banana")
        substrings_dfa = DFA.from_substrings(input_symbols, {"banana", "nano"})

        self.assertEqual(substring_dfa, substrings_dfa)

        self.assertEqual(
            ~substrings_dfa,
            DFA.from_substrings(input_symbols, {"banana", "nano"}, contains=False),
        )

        m = 50
        n = 50
        input_symbols = {"a", "b"}
        language = {("a" * i + "b" * j) for i, j in product(range(n), range(m))}

        equiv_dfa = DFA.from_substrings(
            input_symbols,
            language,
        )

        res_dfa = DFA.empty_language(input_symbols)
        for string in language:
            res_dfa |= DFA.from_substring(input_symbols, string)

        self.assertEqual(equiv_dfa, res_dfa)

    @parameterized.expand((True, False))
    def test_contains_subsequence(self, as_partial: bool) -> None:
        input_symbols = {"a", "n", "o", "b"}

        equiv_dfa = DFA(
            states={"", "n", "na", "nan", "nano"},
            input_symbols=input_symbols,
            transitions={
                "": {"a": "", "n": "n", "o": "", "b": ""},
                "n": {"a": "na", "n": "n", "o": "n", "b": "n"},
                "na": {"a": "na", "n": "nan", "o": "na", "b": "na"},
                "nan": {"a": "nan", "n": "nan", "o": "nano", "b": "nan"},
                "nano": {"a": "nano", "n": "nano", "o": "nano", "b": "nano"},
            },
            initial_state="",
            final_states={"nano"},
        )

        subsequence_dfa = DFA.from_subsequence(input_symbols, "nano")
        self.assertEqual(
            len(subsequence_dfa.states), len(subsequence_dfa.minify().states)
        )

        self.assertEqual(len(subsequence_dfa.states), len(equiv_dfa.states))
        self.assertEqual(subsequence_dfa, equiv_dfa)

        subset_dfa = DFA.from_finite_language(
            input_symbols,
            {"naooono", "bananano", "onbaonbo", "ooonano"},
            as_partial,
        )
        self.assertTrue(subset_dfa < subsequence_dfa)

        substring_dfa = DFA.from_substring(
            input_symbols,
            "nano",
        )
        self.assertTrue(substring_dfa < subsequence_dfa)

        self.assertEqual(
            ~subsequence_dfa,
            DFA.from_subsequence(input_symbols, "nano", contains=False),
        )
