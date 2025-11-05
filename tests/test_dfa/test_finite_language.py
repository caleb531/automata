"""Finite-language oriented DFA tests."""

from itertools import product

from parameterized import parameterized  # type: ignore

from automata.fa.dfa import DFA
from tests.test_dfa.base import DfaTestCase


class TestDfaFiniteLanguage(DfaTestCase):
    """Validate helpers specific to finite DFAs."""

    @parameterized.expand((True, False))
    def test_minimal_finite_language(self, as_partial: bool) -> None:
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

        equiv_dfa = DFA(
            states=set(range(10)),
            input_symbols={"a", "b"},
            transitions={
                0: {"a": 0, "b": 0},
                1: {"a": 2, "b": 3},
                2: {"a": 4, "b": 5},
                3: {"a": 7, "b": 5},
                4: {"a": 9, "b": 7},
                5: {"a": 7, "b": 6},
                6: {"a": 8, "b": 0},
                7: {"a": 9, "b": 8},
                8: {"a": 0, "b": 9},
                9: {"a": 0, "b": 0},
            },
            initial_state=1,
            final_states={4, 9},
        )

        if as_partial:
            equiv_dfa = equiv_dfa.to_partial()

        minimal_dfa = DFA.from_finite_language(
            {"a", "b"}, language, as_partial=as_partial
        )

        self.assertEqual(len(minimal_dfa.states), len(equiv_dfa.states))
        self.assertEqual(minimal_dfa, equiv_dfa)

    @parameterized.expand((True, False))
    def test_minimal_finite_language_large(self, as_partial: bool) -> None:
        m = 50
        n = 50
        language = {("a" * i + "b" * j) for i, j in product(range(n), range(m))}

        equiv_dfa = DFA.from_finite_language(
            {"a", "b"}, language, as_partial=as_partial
        )
        minimal_dfa = equiv_dfa.minify()

        self.assertEqual(equiv_dfa, minimal_dfa)
        self.assertEqual(len(equiv_dfa.states), len(minimal_dfa.states))
        dfa_language = {word for word in equiv_dfa}
        self.assertEqual(dfa_language, language)

    def test_dfa_repr(self) -> None:
        dfa = DFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
            allow_partial=False,
        )
        self.assertEqual(
            repr(dfa),
            "DFA(states={'q0'}, input_symbols={'a'}, transitions={'q0': {'a': 'q0'}}, "
            "initial_state='q0', final_states={'q0'}, allow_partial=False)",
        )

    def test_dfa_repr_retain_names(self) -> None:
        dfa1 = DFA.from_finite_language(set("abcd"), {"abcd", "dcba"})
        dfa2 = dfa1.minify(retain_names=True)
        self.assertTrue(repr(dfa2))


__all__ = ["TestDfaFiniteLanguage"]
