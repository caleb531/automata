"""Classes and functions for testing the behavior of GNFAs."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON


class TestGNFA(test_fa.TestFA):
    """A test class for testing generalized nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

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

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidRegexError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "c", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q3": "a", "q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q3",
                final_state="q_f",
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q3",
            )

    def test_validate_final_state_transition(self) -> None:
        """Should raise error if there are transitions from final state"""
        with self.assertRaises(exceptions.InvalidStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                    "q_f": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_missing_state(self) -> None:
        """Should raise an error if some transitions are missing."""
        with self.assertRaises(exceptions.MissingStateError):
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_validate_incomplete_transitions(self) -> None:
        """
        Should raise error if transitions from (except final state)
        and to (except initial state) every state is missing.
        """
        with self.assertRaises(exceptions.MissingStateError):
            # del gnfa.transitions['q1']['q0']
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": ""},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

        with self.assertRaises(exceptions.MissingStateError):
            # del gnfa.transitions['q_in']['q_f']
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {"q0": "", "q2": None, "q1": None},
                },
                initial_state="q_in",
                final_state="q_f",
            )

        with self.assertRaises(exceptions.InvalidStateError):
            # gnfa.transitions['q_in']['q5'] = {}
            GNFA(
                states={"q_in", "q_f", "q0", "q1", "q2"},
                input_symbols={"a", "b"},
                transitions={
                    "q0": {"q1": "a", "q_f": None, "q2": None, "q0": None},
                    "q1": {"q1": "a", "q2": "", "q_f": "", "q0": None},
                    "q2": {"q0": "b", "q_f": None, "q2": None, "q1": None},
                    "q_in": {
                        "q0": "",
                        "q_f": None,
                        "q2": None,
                        "q1": None,
                        "q5": {},  # type: ignore
                    },
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_from_dfa(self) -> None:
        """
        Check if GNFA is generated properly from DFA
        """

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

    def test_to_regex(self) -> None:
        """
        We generate GNFA from DFA then convert it to regex
        then generate NFA from regex (already tested method)
        and check for equivalence of NFA and previous DFA
        """
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

            # Test equality under NFA regex conversion
            self.assertEqual(nfa_1, nfa_2)

            dfa_1 = DFA.from_nfa(nfa_1)
            gnfa_2 = GNFA.from_dfa(dfa_1)
            regex_2 = gnfa_2.to_regex()
            dfa_2 = DFA.from_nfa(NFA.from_regex(regex_2))

            # Test equality through DFA regex conversion
            self.assertEqual(dfa_1, dfa_2)

    def test_gnfa_deterministic(self) -> None:
        """
        Check for deterministic conversion to GNFA.
        From https://github.com/caleb531/automata/issues/231
        """

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
                    "q1": {gt_symbols["Close"]: {"q0"}, gt_symbols["Send_msg"]: {"q2"}},
                    "q2": {gt_symbols["Ack"]: {"q1", "q0"}},
                },
                initial_state="q0",
                final_states={"q0", "q1", "q2"},
            ),
            retain_names=True,
        )

        # Repeat the test multiple times to account for possible non-determinism.
        num_reps = 1_000
        starting_gnfa = GNFA.from_dfa(gt_dfa)

        for _ in range(num_reps):
            regex = starting_gnfa.to_regex()
            self.assertEqual("(0(12(12)*(30|0)|30)*(12(12)*(3|1?)|(3|1?)))?", regex)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram(self) -> None:
        """
        Should construct the diagram for a GNFA.
        """

        graph = self.gnfa.show_diagram()

        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.gnfa.states).issubset(node_names))
        self.assertEqual(len(self.gnfa.states) + 1, len(node_names))

        for state in self.dfa.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.gnfa.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q_in", "ε", "q0"),
            ("q1", "ε", "q2"),
            ("q1", "ε", "q_f"),
            ("q1", "a", "q1"),
            ("q2", "b", "q0"),
            ("q0", "a", "q1"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }

        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, self.gnfa.initial_state)
        self.assertTrue(source not in self.gnfa.states)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a NFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, "test_gnfa.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.gnfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)
