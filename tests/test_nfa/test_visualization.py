"""Visualization and input-path utilities for NFAs."""

import os
import unittest
from itertools import product

from automata.fa.nfa import NFA
from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_nfa.base import NFATestCase


@unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
class TestNFAVisualization(NFATestCase):
    """Ensure diagram rendering behaves as expected."""

    def test_show_diagram_initial_final_same(self) -> None:
        graph = self.nfa.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.nfa.states).issubset(node_names))
        self.assertEqual(len(self.nfa.states) + 1, len(node_names))

        for state in self.dfa.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.nfa.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", "a", "q1"),
            ("q1", "a", "q1"),
            ("q1", "ε", "q2"),
            ("q2", "b", "q0"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }

        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, self.nfa.initial_state)
        self.assertTrue(source not in self.nfa.states)

    def test_show_diagram_read_input(self) -> None:
        input_strings = ["ababa", "bba", "aabba", "baaab", "bbaab", ""]

        for input_string in input_strings:
            graph = self.nfa.show_diagram(input_str=input_string)

            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            colored_edges.sort(key=lambda edge: edge.attr["label"][2:])

            edge_pairs = [
                edge[0:2] for edge in self.nfa._get_input_path(input_string)[0]
            ]

            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_write_file(self) -> None:
        diagram_path = os.path.join(self.temp_dir_path, "test_dfa.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.nfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)


class TestNFAInputPath(NFATestCase):
    """Validate path helpers that power visualization overlays."""

    def test_get_input_path(self) -> None:
        nfa2 = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"": {"q1"}, "b": {"q0"}},
                "q1": {"a": {"q2"}, "": {"q0"}},
                "q2": {"b": {"q2"}, "a": {"q1"}},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        nfa3 = NFA.from_regex("(abab|aabba)*bba*bb")

        input_strings = [
            "ababa",
            "bba",
            "aabba",
            "baaab",
            "bbaab",
            "",
            "bbbb",
            "bbaabb",
        ]
        nfas = [self.nfa, nfa2, nfa3]

        for input_str, nfa in product(input_strings, nfas):
            input_path, was_accepted = nfa._get_input_path(input_str)
            self.assertEqual(was_accepted, nfa.accepts_input(input_str))

            last_vtx = None

            for start_vtx, end_vtx, symbol in input_path:
                last_vtx = end_vtx
                self.assertIn(end_vtx, nfa.transitions[start_vtx][symbol])

            self.assertEqual(last_vtx in nfa.final_states, was_accepted)

    def test_input_path_optimality(self) -> None:
        nfa = NFA(
            states=set(range(6)),
            input_symbols=set("01"),
            transitions={
                0: {"0": {1, 2}},
                1: {"": {3}},
                2: {"1": {4}},
                3: {"1": {4}},
                4: {"": {5}},
                5: {},
            },
            initial_state=0,
            final_states={5},
        )

        input_str = "01"

        input_path, was_accepted = nfa._get_input_path(input_str)
        self.assertEqual(was_accepted, nfa.accepts_input(input_str))
        self.assertEqual(len(input_path), 3)
