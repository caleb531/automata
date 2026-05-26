"""Tests covering DFA conversions from other automata representations."""

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from tests.test_dfa.base import DFATestCase


class TestDFAConversions(DFATestCase):
    """Ensure DFAs interoperate with NFAs and partial constructions."""

    def test_init_nfa_simple(self) -> None:
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": {"q0", "q1"}}, "q1": {"1": {"q2"}}, "q2": {}},
            initial_state="q0",
            final_states={"q2"},
        )
        dfa = DFA.from_nfa(nfa, retain_names=True, minify=False).to_complete(
            frozenset()
        )
        self.assertEqual(
            dfa.states,
            {
                frozenset(),
                frozenset(("q0",)),
                frozenset(("q0", "q1")),
                frozenset(("q2",)),
            },
        )
        self.assertEqual(dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(): {"0": frozenset(), "1": frozenset()},
                frozenset(("q0",)): {"0": frozenset(("q0", "q1")), "1": frozenset()},
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q2",)),
                },
                frozenset(("q2",)): {"0": frozenset(), "1": frozenset()},
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(dfa.final_states, {frozenset(("q2",))})

    def test_init_nfa_more_complex(self) -> None:
        """Should convert to a DFA a more complex NFA."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": {"q0", "q1"}, "1": {"q0"}},
                "q1": {"0": {"q1"}, "1": {"q2"}},
                "q2": {"0": {"q2"}, "1": {"q1"}},
            },
            initial_state="q0",
            final_states={"q2"},
        )
        dfa = DFA.from_nfa(nfa, retain_names=True, minify=False)
        self.assertEqual(
            dfa.states,
            frozenset(
                {
                    frozenset(("q0",)),
                    frozenset(("q0", "q1")),
                    frozenset(("q0", "q2")),
                    frozenset(("q0", "q1", "q2")),
                }
            ),
        )
        self.assertEqual(dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(("q0",)): {
                    "1": frozenset(("q0",)),
                    "0": frozenset(("q0", "q1")),
                },
                frozenset(("q0", "q1")): {
                    "1": frozenset(("q0", "q2")),
                    "0": frozenset(("q0", "q1")),
                },
                frozenset(("q0", "q2")): {
                    "1": frozenset(("q0", "q1")),
                    "0": frozenset(("q0", "q1", "q2")),
                },
                frozenset(("q0", "q1", "q2")): {
                    "1": frozenset(("q0", "q1", "q2")),
                    "0": frozenset(("q0", "q1", "q2")),
                },
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(
            dfa.final_states, {frozenset(("q0", "q1", "q2")), frozenset(("q0", "q2"))}
        )

    def test_init_nfa_lambda_transition(self) -> None:
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA.from_nfa(self.nfa, retain_names=True, minify=False).to_complete(
            frozenset()
        )
        self.assertEqual(
            dfa.states,
            frozenset({frozenset(), frozenset(("q0",)), frozenset(("q1", "q2"))}),
        )
        self.assertEqual(dfa.input_symbols, {"a", "b"})
        self.assertEqual(
            dfa.transitions,
            {
                frozenset(): {"a": frozenset(), "b": frozenset()},
                frozenset(("q0",)): {"a": frozenset(("q1", "q2")), "b": frozenset()},
                frozenset(("q1", "q2")): {
                    "a": frozenset(("q1", "q2")),
                    "b": frozenset(("q0",)),
                },
            },
        )
        self.assertEqual(dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(dfa.final_states, {frozenset(("q1", "q2"))})

    def test_nfa_to_dfa_with_lambda_transitions(self) -> None:
        """Test NFA->DFA when initial state has lambda transitions"""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={"q0": {"": {"q2"}}, "q1": {"a": {"q1"}}, "q2": {"a": {"q1"}}},
            initial_state="q0",
            final_states={"q1"},
        )
        dfa = DFA.from_nfa(nfa, retain_names=True, minify=False)
        self.assertEqual(dfa.read_input("a"), frozenset(("q1",)))

    def test_partial_dfa(self) -> None:
        """Should allow for partial DFA when flag is set"""
        dfa = DFA(
            states={"", "a", "b", "aa", "bb", "ab", "ba"},
            input_symbols={"a", "b"},
            transitions={
                "": {"a": "a", "b": "b"},
                "a": {"b": "ab", "a": "aa"},
                "b": {"b": "bb"},
                "aa": {"a": "aa", "b": "ab"},
                "bb": {"a": "ba"},
                "ab": {"b": "bb"},
                "ba": {"a": "aa"},
            },
            initial_state="",
            final_states={"aa"},
            allow_partial=True,
        )
        self.assertEqual(dfa.read_input("aa"), "aa")
