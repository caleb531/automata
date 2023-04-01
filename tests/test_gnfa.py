#!/usr/bin/env python3
"""Classes and functions for testing the behavior of GNFAs."""
import os
import tempfile
from unittest.mock import patch

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA


class TestGNFA(test_fa.TestFA):
    """A test class for testing generalized nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_gnfa(self):
        """Should copy GNFA if passed into NFA constructor."""
        new_gnfa = self.gnfa.copy()
        self.assertIsNot(new_gnfa, self.gnfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            GNFA(
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_state="q1",
            )

    def test_copy_gnfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_gnfa = self.gnfa.copy()
        self.assertIsNot(new_gnfa, self.gnfa)

    def test_gnfa_immutable_attr_set(self):
        with self.assertRaises(AttributeError):
            self.gnfa.states = {}

    def test_gnfa_immutable_attr_del(self):
        with self.assertRaises(AttributeError):
            del self.gnfa.states

    def test_init_dfa(self):
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

    def test_init_nfa(self):
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
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        self.gnfa.copy()
        validate.assert_called_once_with()

    def test_validate_invalid_symbol(self):
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

    def test_validate_invalid_state(self):
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

    def test_validate_invalid_initial_state(self):
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

    def test_validate_initial_state_transitions(self):
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

    def test_validate_invalid_final_state(self):
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

    def test_validate_final_state_transition(self):
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

    def test_validate_missing_state(self):
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

    def test_validate_incomplete_transitions(self):
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
                    "q_in": {"q0": "", "q_f": None, "q2": None, "q1": None, "q5": {}},
                },
                initial_state="q_in",
                final_state="q_f",
            )

    def test_from_dfa(self):
        """
        Check if GNFA is generated properly from DFA
        """

        dfa = DFA(
            states={0, 1, 2, 4},
            input_symbols={"a", "b"},
            initial_state=0,
            final_states={4},
            transitions={0: {"a": 1, "b": 2}, 1: {"a": 2, "b": 2}, 2: {"b": 4}},
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

    def test_from_dfa_single_state(self):
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

    def test_from_nfa_single_state(self):
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

    def test_from_nfa(self):
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

    def test_to_regex(self):
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

    def test_read_input_step_not_implemented(self):
        """Should not implement read_input_stepwise() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.read_input_stepwise("aaa")

    def test_union_not_implemented(self):
        """Should not implement union() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.union(self.gnfa)

    def test_concatenate_not_implemented(self):
        """Should not implement concatenate() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.concatenate(self.gnfa)

    def test_kleene_star_not_implemented(self):
        """Should not implement kleene_star() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.kleene_star()

    def test_option_not_implemented(self):
        """Should not implement option() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.option()

    def test_reverse_not_implemented(self):
        """Should not implement reverse() for GNFA."""
        with self.assertRaises(NotImplementedError):
            self.gnfa.reverse()

    def test_eq_not_implemented(self):
        """Should not implement equality for GNFA."""
        self.assertNotEqual(self.gnfa, GNFA.from_nfa(self.nfa))

    def test_show_diagram_showNone(self):
        """
        Should construct the diagram for a GNFA when show_None = False
        """

        gnfa = self.gnfa

        graph = gnfa.show_diagram(show_None=False)
        self.assertEqual({node.get_name() for node in graph.get_nodes()}, gnfa.states)
        self.assertEqual(graph.get_node(gnfa.initial_state)[0].get_style(), "filled")
        self.assertEqual(graph.get_node(gnfa.final_state)[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node("q2")[0].get_peripheries(), None)
        self.assertEqual(
            {
                (edge.get_source(), edge.get_label(), edge.get_destination())
                for edge in graph.get_edges()
            },
            {
                ("q0", "a", "q1"),
                ("q1", "a", "q1"),
                ("q1", "", "q2"),
                ("q1", "", "q_f"),
                ("q2", "b", "q0"),
                ("q_in", "", "q0"),
            },
        )

    def test_show_diagram(self):
        """
        Should construct the diagram for a GNFA when show_None = True
        """

        gnfa = self.gnfa

        graph = gnfa.show_diagram()
        self.assertEqual({node.get_name() for node in graph.get_nodes()}, gnfa.states)
        self.assertEqual(graph.get_node(gnfa.initial_state)[0].get_style(), "filled")
        self.assertEqual(graph.get_node(gnfa.final_state)[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node("q2")[0].get_peripheries(), None)
        self.assertEqual(
            {
                (edge.get_source(), edge.get_label(), edge.get_destination())
                for edge in graph.get_edges()
            },
            {
                ("q_in", "", "q0"),
                ("q0", "ø", "q2"),
                ("q1", "", "q2"),
                ("q0", "ø", "q_f"),
                ("q1", "", "q_f"),
                ("q_in", "ø", "q2"),
                ("q_in", "ø", "q1"),
                ("q1", "a", "q1"),
                ("q2", "b", "q0"),
                ("q2", "ø", "q2"),
                ("q_in", "ø", "q_f"),
                ("q2", "ø", "q1"),
                ("q0", "ø", "q0"),
                ("q2", "ø", "q_f"),
                ("q0", "a", "q1"),
                ("q1", "ø", "q0"),
            },
        )

    def test_show_diagram_write_file(self):
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
