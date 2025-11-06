"""Edit-distance style NFA constructor tests."""

import string
from itertools import product

from automata.fa.nfa import NFA
from tests.test_nfa.base import NfaTestCase


class TestNfaEditDistance(NfaTestCase):
    """Validate the family of edit-distance NFA builders."""

    def test_nfa_levenshtein_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (1, 1), (0, 1)},
                    "a": {(0, 1), (1, 1)},
                    "o": {(0, 1), (1, 1)},
                    "d": {(0, 1), (1, 1)},
                    "": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (1, 2), (0, 2)},
                    "a": {(0, 2), (1, 2)},
                    "o": {(0, 2), (1, 2)},
                    "d": {(0, 2), (1, 2)},
                    "": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(1, 1), (2, 0), (2, 1)},
                    "a": {(1, 1), (2, 1)},
                    "f": {(1, 1), (2, 1)},
                    "d": {(1, 1), (2, 1)},
                    "": {(2, 1)},
                },
                (1, 1): {
                    "o": {(1, 2), (2, 1), (2, 2)},
                    "a": {(1, 2), (2, 2)},
                    "f": {(1, 2), (2, 2)},
                    "d": {(1, 2), (2, 2)},
                    "": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(3, 1), (2, 1), (3, 0)},
                    "a": {(3, 1), (2, 1)},
                    "f": {(3, 1), (2, 1)},
                    "d": {(3, 1), (2, 1)},
                    "": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (3, 2), (2, 2)},
                    "a": {(3, 2), (2, 2)},
                    "f": {(3, 2), (2, 2)},
                    "d": {(3, 2), (2, 2)},
                    "": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(3, 1), (4, 0), (4, 1)},
                    "a": {(3, 1), (4, 1)},
                    "f": {(3, 1), (4, 1)},
                    "o": {(3, 1), (4, 1)},
                    "": {(4, 1)},
                },
                (3, 1): {
                    "d": {(3, 2), (4, 1), (4, 2)},
                    "a": {(3, 2), (4, 2)},
                    "f": {(3, 2), (4, 2)},
                    "o": {(3, 2), (4, 2)},
                    "": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {"a": {(4, 1)}, "f": {(4, 1)}, "o": {(4, 1)}, "d": {(4, 1)}},
                (4, 1): {"a": {(4, 2)}, "f": {(4, 2)}, "o": {(4, 2)}, "d": {(4, 2)}},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(nfa, NFA.edit_distance(alphabet, "food", 2))

        nice_nfa = NFA.edit_distance(set(string.ascii_lowercase), "nice", 1)

        self.assertFalse(nice_nfa.accepts_input("food"))

        close_strings = [
            "anice",
            "bice",
            "dice",
            "fice",
            "ice",
            "mice",
            "nace",
            "nice",
            "niche",
            "nick",
            "nide",
            "niece",
            "nife",
            "nile",
            "nine",
            "niue",
            "pice",
            "rice",
            "sice",
            "tice",
            "unice",
            "vice",
            "wice",
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(alphabet, "food", -1)
        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(
                alphabet,
                "food",
                2,
                insertion=False,
                deletion=False,
                substitution=False,
            )

    def test_nfa_hamming_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (1, 1)},
                    "d": {(1, 1)},
                    "o": {(1, 1)},
                    "a": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (1, 2)},
                    "d": {(1, 2)},
                    "o": {(1, 2)},
                    "a": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(2, 0), (2, 1)},
                    "d": {(2, 1)},
                    "a": {(2, 1)},
                    "f": {(2, 1)},
                },
                (1, 1): {
                    "o": {(2, 1), (2, 2)},
                    "d": {(2, 2)},
                    "a": {(2, 2)},
                    "f": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(3, 1), (3, 0)},
                    "d": {(3, 1)},
                    "a": {(3, 1)},
                    "f": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (3, 2)},
                    "d": {(3, 2)},
                    "a": {(3, 2)},
                    "f": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(4, 0), (4, 1)},
                    "o": {(4, 1)},
                    "a": {(4, 1)},
                    "f": {(4, 1)},
                },
                (3, 1): {
                    "d": {(4, 1), (4, 2)},
                    "o": {(4, 2)},
                    "a": {(4, 2)},
                    "f": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {},
                (4, 1): {},
                (4, 2): {},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(
            nfa,
            NFA.edit_distance(
                alphabet,
                "food",
                2,
                insertion=False,
                deletion=False,
            ),
        )

        nice_nfa = NFA.edit_distance(
            set(string.ascii_lowercase),
            "nice",
            1,
            insertion=False,
            deletion=False,
        )

        self.assertFalse(nice_nfa.accepts_input("food"))

        close_strings = [
            "bice",
            "dice",
            "fice",
            "mice",
            "nace",
            "nice",
            "nick",
            "nide",
            "nife",
            "nile",
            "nine",
            "niue",
            "pice",
            "rice",
            "sice",
            "tice",
            "vice",
            "wice",
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        close_strings_insertion_deletion = [
            "anice",
            "nicee",
            "niece",
            "unice",
            "niace",
            "ice",
            "nce",
            "nic",
        ]

        for close_string in close_strings_insertion_deletion:
            self.assertFalse(nice_nfa.accepts_input(close_string))

    def test_nfa_LCS_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (0, 1)},
                    "d": {(0, 1)},
                    "a": {(0, 1)},
                    "o": {(0, 1)},
                    "": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (0, 2)},
                    "d": {(0, 2)},
                    "a": {(0, 2)},
                    "o": {(0, 2)},
                    "": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(1, 1), (2, 0)},
                    "d": {(1, 1)},
                    "a": {(1, 1)},
                    "f": {(1, 1)},
                    "": {(2, 1)},
                },
                (1, 1): {
                    "o": {(1, 2), (2, 1)},
                    "d": {(1, 2)},
                    "a": {(1, 2)},
                    "f": {(1, 2)},
                    "": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(2, 1), (3, 0)},
                    "d": {(2, 1)},
                    "a": {(2, 1)},
                    "f": {(2, 1)},
                    "": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (2, 2)},
                    "d": {(2, 2)},
                    "a": {(2, 2)},
                    "f": {(2, 2)},
                    "": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(3, 1), (4, 0)},
                    "a": {(3, 1)},
                    "f": {(3, 1)},
                    "o": {(3, 1)},
                    "": {(4, 1)},
                },
                (3, 1): {
                    "d": {(3, 2), (4, 1)},
                    "a": {(3, 2)},
                    "f": {(3, 2)},
                    "o": {(3, 2)},
                    "": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {"d": {(4, 1)}, "a": {(4, 1)}, "f": {(4, 1)}, "o": {(4, 1)}},
                (4, 1): {"d": {(4, 2)}, "a": {(4, 2)}, "f": {(4, 2)}, "o": {(4, 2)}},
                (4, 2): {},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(
            nfa,
            NFA.edit_distance(alphabet, "food", 2, substitution=False),
        )

        close_strings_substitution = ["tice", "nick", "noce"]
        close_strings_insertion = ["anice", "nicee", "niece", "unice", "niace"]
        close_strings_deletion = ["ice", "nce", "nic"]

        nice_nfa_insertion = NFA.edit_distance(
            set(string.ascii_lowercase),
            "nice",
            1,
            insertion=True,
            substitution=False,
            deletion=False,
        )
        nice_nfa_deletion = NFA.edit_distance(
            set(string.ascii_lowercase),
            "nice",
            1,
            deletion=True,
            substitution=False,
            insertion=False,
        )

        for close_string in close_strings_substitution:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_insertion:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertTrue(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_deletion:
            self.assertTrue(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))


__all__ = ["TestNfaEditDistance"]
