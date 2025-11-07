"""Regex round-trip tests for generalized NFAs."""

from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
from tests.test_gnfa.base import GNFATestCase


class TestGNFARegex(GNFATestCase):
    """Verify regex conversions for GNFA instances."""

    def test_to_regex(self) -> None:
        """Should produce equivalent automata when converting via regex."""
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
