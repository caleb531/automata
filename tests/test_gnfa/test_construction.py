"""Construction and conversion tests for generalized NFAs."""

from unittest.mock import MagicMock, patch

from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
from tests.test_gnfa.base import GNFATestCase


class TestGNFAConstruction(GNFATestCase):
    """Cover initialization helpers, conversions, and cloning."""

    def test_methods_not_implemented(self) -> None:
        """Should raise NotImplementedError when calling non-implemented methods."""
        abstract_methods = {
            "_get_input_path": (GNFA, ""),
            "read_input_stepwise": (GNFA, ""),
        }
        for method_name, method_args in abstract_methods.items():
            with self.assertRaises(NotImplementedError):
                getattr(GNFA, method_name)(*method_args)

    def test_init_gnfa(self) -> None:
        """Should copy GNFA if passed into NFA constructor."""
        new_gnfa = self.gnfa.copy()
        self.assertIsNot(new_gnfa, self.gnfa)

    def test_init_nfa_missing_formal_params(self) -> None:
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            GNFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_state="q1",
            )

    def test_copy_gnfa(self) -> None:
        """Should create exact copy of NFA if copy() method is called."""
        new_gnfa = self.gnfa.copy()
        self.assertIsNot(new_gnfa, self.gnfa)

    def test_gnfa_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.gnfa.states = {}  # type: ignore

    def test_gnfa_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.gnfa.states

    def test_init_dfa(self) -> None:
        """Should convert DFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_dfa(self.dfa)
        self.assertEqual(gnfa.states, {0, 1, "q2", "q0", "q1"})
        self.assertEqual(gnfa.input_symbols, {"0", "1"})
        self.assertEqual(
            gnfa.transitions,
            {
                "q0": {"q0": "0", "q1": "1", 1: None, "q2": None},
                "q1": {"q0": "0", "q2": "1", 1: "", "q1": None},
                "q2": {"q2": "0", "q1": "1", 1: None, "q0": None},
                0: {"q0": "", 1: None, "q1": None, "q2": None},
            },
        )
        self.assertEqual(gnfa.initial_state, 0)

    def test_init_nfa(self) -> None:
        """Should convert NFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_nfa(self.nfa)
        self.assertEqual(gnfa.states, {0, 1, "q0", "q1", "q2"})
        self.assertEqual(gnfa.input_symbols, {"b", "a"})
        self.assertEqual(
            gnfa.transitions,
            {
                0: {1: None, "q0": "", "q1": None, "q2": None},
                "q0": {1: None, "q0": None, "q1": "a", "q2": None},
                "q1": {1: "", "q0": None, "q1": "a", "q2": ""},
                "q2": {1: None, "q0": "b", "q1": None, "q2": None},
            },
        )
        self.assertEqual(gnfa.initial_state, 0)

    @patch("automata.fa.gnfa.GNFA.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate NFA when initialized."""
        self.gnfa.copy()
        validate.assert_called_once_with()

    def test_from_dfa(self) -> None:
        """Check if GNFA is generated properly from DFA"""
        dfa = DFA(
            states={0, 1, 2, 4},
            input_symbols={"a", "b"},
            initial_state=0,
            final_states={4},
            transitions={
                0: {"a": 1, "b": 2},
                1: {"a": 2, "b": 2},
                2: {"b": 4},
                4: {},
            },
            allow_partial=True,
        )

        gnfa = GNFA.from_dfa(dfa)
        gnfa2 = GNFA(
            states={0, 1, 2, 3, 4, 5},
            input_symbols={"a", "b"},
            initial_state=3,
            final_state=5,
            transitions={
                0: {1: "a", 2: "b", 0: None, 4: None, 5: None},
                1: {2: "a|b", 0: None, 1: None, 4: None, 5: None},
                2: {4: "b", 0: None, 1: None, 2: None, 5: None},
                3: {0: "", 1: None, 2: None, 4: None, 5: None},
                4: {5: "", 0: None, 1: None, 2: None, 4: None},
            },
        )

        self.assertEqual(gnfa.input_parameters, gnfa2.input_parameters)

    def test_from_dfa_single_state(self) -> None:
        """Should create a GNFA when converting a single-state DFA."""
        nfa = NFA.from_regex("")
        dfa = DFA.from_nfa(nfa)
        gnfa = GNFA.from_dfa(dfa)

        gnfa2 = GNFA(
            states={0, 1, "{0}"},
            input_symbols=set(),
            initial_state=0,
            final_state=1,
            transitions={"{0}": {1: "", "{0}": None}, 0: {"{0}": "", 1: None}},
        )

        self.assertEqual(gnfa.to_regex(), gnfa2.to_regex())

    def test_from_nfa_single_state(self) -> None:
        """Should create a GNFA when converting a single-state NFA."""
        nfa = NFA.from_regex("")
        gnfa = GNFA.from_nfa(nfa)

        gnfa2 = GNFA(
            states={0, 1, 2},
            input_symbols=set(),
            initial_state=1,
            final_state=2,
            transitions={0: {2: "", 0: None}, 1: {0: "", 2: None}},
        )

        self.assertEqual(gnfa.to_regex(), gnfa2.to_regex())

    def test_from_nfa(self) -> None:
        """Should convert NFA to GNFA properly"""
        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={"a", "b"},
            transitions={
                0: {"a": {1}, "b": {1}, "": {1}},
                1: {"a": {1, 2}, "": {2, 4}},
                2: {"": {0}, "b": {0, 4}},
            },
            initial_state=0,
            final_states={4},
        )

        gnfa = GNFA.from_nfa(nfa)

        gnfa2 = GNFA(
            states={0, 1, 2, 3, 4, 5},
            initial_state=3,
            final_state=5,
            input_symbols={"a", "b"},
            transitions={
                0: {1: "(a|b)?", 0: None, 2: None, 4: None, 5: None},
                1: {1: "a", 2: "a?", 4: "", 0: None, 5: None},
                2: {0: "b?", 4: "b", 1: None, 2: None, 5: None},
                4: {5: "", 0: None, 1: None, 2: None, 4: None},
                3: {0: "", 1: None, 2: None, 4: None, 5: None},
            },
        )

        self.assertEqual(gnfa.input_parameters, gnfa2.input_parameters)

    def test_gnfa_deterministic(self) -> None:
        """Check for deterministic conversion to GNFA.
        From https://github.com/caleb531/automata/issues/231"""
        gt_symbols = {"Connect": "0", "Send_msg": "1", "Ack": "2", "Close": "3"}
        gt_dfa = DFA.from_nfa(
            NFA(
                states={"q0", "q1", "q2"},
                input_symbols={
                    gt_symbols["Connect"],
                    gt_symbols["Send_msg"],
                    gt_symbols["Close"],
                    gt_symbols["Ack"],
                },
                transitions={
                    "q0": {gt_symbols["Connect"]: {"q1"}},
                    "q1": {
                        gt_symbols["Close"]: {"q0"},
                        gt_symbols["Send_msg"]: {"q2"},
                    },
                    "q2": {gt_symbols["Ack"]: {"q1", "q0"}},
                },
                initial_state="q0",
                final_states={"q0", "q1", "q2"},
            ),
            retain_names=True,
        )

        num_reps = 1_000
        starting_gnfa = GNFA.from_dfa(gt_dfa)

        for _ in range(num_reps):
            regex = starting_gnfa.to_regex()
            self.assertEqual("(0(12(12)*(30|0)|30)*(12(12)*(3|1?)|(3|1?)))?", regex)
