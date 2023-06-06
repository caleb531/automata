#!/usr/bin/env python3
"""Classes and functions for testing the behavior of both DFAs and NFAs."""

import unittest

from automata.fa.dfa import DFA
from automata.fa.fa import FA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA


class TestFA(unittest.TestCase):
    """A test class for testing all finite automata."""

    dfa: DFA
    nfa: NFA
    gnfa: GNFA

    def setUp(self) -> None:
        """Reset test automata before every test function."""
        # DFA which matches all binary strings ending in an odd number of '1's
        self.dfa = DFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q0", "1": "q1"},
                "q1": {"0": "q0", "1": "q2"},
                "q2": {"0": "q2", "1": "q1"},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        # NFA which matches strings beginning with 'a', ending with 'a', and
        # containing no consecutive 'b's
        self.nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": {"q1"}},
                "q1": {"a": {"q1"}, "": {"q2"}},
                "q2": {"b": {"q0"}},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        # GNFA which matches strings beginning with 'a', ending with 'a', and containing
        # no consecutive 'b's
        self.gnfa = GNFA(
            states={"q_in", "q_f", "q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
            },
            initial_state="q_in",
            final_state="q_f",
        )


class TestFAAbstract(unittest.TestCase):
    def test_abstract_methods_not_implemented(self) -> None:
        """Should raise NotImplementedError when calling abstract methods."""

        with self.assertRaises(NotImplementedError):
            getattr(FA, "_get_input_path")(FA, "")
