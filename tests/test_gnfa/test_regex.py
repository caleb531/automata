"""Regex round-trip tests for generalized NFAs."""

from itertools import product
from typing import Optional

from parameterized import parameterized

from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
from tests.test_gnfa.base import GNFATestCase


class TestGNFARegex(GNFATestCase):
    """Verify regex conversions for GNFA instances."""

    def test_to_regex(self) -> None:
        """We generate GNFA from DFA then convert it to regex
        then generate NFA from regex (already tested method)
        and check for equivalence of NFA and previous DFA"""
        regex_strings = [
            "a*",
            "aa*b|bba*|(cc*)(bb+)",
            "a(aaa*bbcd|abbcd)d*|aa*bb(dcc*|(d|c)b|a?bb(dcc*|(d|c)))ab(c|d)*(ccd)?",
        ]

        for regex_str in regex_strings:
            nfa_1 = NFA.from_regex(regex_str)
            gnfa_1 = GNFA.from_nfa(nfa_1)
            regex_1 = gnfa_1.to_regex()
            nfa_2 = NFA.from_regex(regex_1)

            self.assertEqual(nfa_1, nfa_2)

            dfa_1 = DFA.from_nfa(nfa_1)
            gnfa_2 = GNFA.from_dfa(dfa_1)
            regex_2 = gnfa_2.to_regex()
            dfa_2 = DFA.from_nfa(NFA.from_regex(regex_2))

            self.assertEqual(dfa_1, dfa_2)

    @parameterized.expand(
        [(None,), ("",), ("a",), ("ab",), ("a|b",), ("a?",), ("(ab)*",)]
    )
    def test_to_regex_epsilon_union(self, existing_path: Optional[str]) -> None:
        """An epsilon path must make an existing alternative optional."""
        gnfa = GNFA(
            states={0, 1, 2},
            input_symbols={"a", "b"},
            transitions={
                0: {1: "", 2: existing_path},
                1: {1: None, 2: ""},
            },
            initial_state=0,
            final_state=2,
        )
        regex = gnfa.to_regex()
        actual = NFA.from_regex(regex, input_symbols={"a", "b"})
        expected_regex = "()" if not existing_path else f"({existing_path})?"
        expected = NFA.from_regex(expected_regex, input_symbols={"a", "b"})
        self.assertEqual(actual, expected)

    def test_to_regex_epsilon_cycle(self) -> None:
        """State elimination must preserve epsilon alternatives inside a cycle."""
        nfa = NFA(
            states={0, 1, 2},
            input_symbols={"a"},
            transitions={0: {"": {1}}, 1: {"a": {2}}, 2: {"": {0}, "a": {1}}},
            initial_state=0,
            final_states={1},
        )
        actual = NFA.from_regex(GNFA.from_nfa(nfa).to_regex(), input_symbols={"a"})
        self.assertEqual(actual, nfa)
        self.assertEqual(actual, NFA.from_regex("a*"))

    def test_to_regex_epsilon_graphs(self) -> None:
        """Round-trip every three-state epsilon graph on a fixed labeled cycle."""
        states = {0, 1, 2}
        edges = list(product(states, repeat=2))
        words = ["a" * length for length in range(7)]
        for mask in range(1 << len(edges)):
            transitions = {
                state: {"a": {(state + 1) % 3}, "": set()} for state in states
            }
            for bit, (source, target) in enumerate(edges):
                if mask & (1 << bit):
                    transitions[source][""].add(target)
            nfa = NFA(
                states=states,
                input_symbols={"a"},
                transitions=transitions,
                initial_state=0,
                final_states={1},
            )
            with self.subTest(mask=mask):
                regex = GNFA.from_nfa(nfa).to_regex()
                actual = NFA.from_regex(regex, input_symbols={"a"})
                self.assertEqual(actual, nfa)
                self.assertEqual(
                    [actual.accepts_input(word) for word in words],
                    [nfa.accepts_input(word) for word in words],
                )
