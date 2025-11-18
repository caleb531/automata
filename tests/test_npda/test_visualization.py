"""Diagram rendering tests for nondeterministic pushdown automata."""

import contextlib
import os
import unittest

from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_npda.base import NPDATestCase


class TestNPDAVisualization(NPDATestCase):
    """Exercise diagram generation and stack-tracing utilities."""

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram(self) -> None:
        """Should construct the diagram for a NPDA"""
        graph = self.npda.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.npda.states).issubset(node_names))
        self.assertEqual(len(self.npda.states) + 1, len(node_names))

        for state in self.npda.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.npda.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", frozenset({"a, A | ε", "b, B | ε"}), "q1"),
            (
                "q0",
                frozenset(
                    {
                        "ε, # | #",
                    }
                ),
                "q2",
            ),
            (
                "q0",
                frozenset(
                    {
                        "a, # | A#",
                        "a, A | AA",
                        "a, B | AB",
                        "b, # | B#",
                        "b, A | BA",
                        "b, B | BB",
                    }
                ),
                "q0",
            ),
            ("q1", frozenset({"a, A | ε", "b, B | ε"}), "q1"),
            (
                "q1",
                frozenset(
                    {
                        "ε, # | #",
                    }
                ),
                "q2",
            ),
        }

        seen_transitions = {
            (
                edge[0],
                frozenset(map(str.strip, edge.attr["label"].split("\n"))),
                edge[1],
            )
            for edge in graph.edges()
        }

        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, frozenset({""}))
        self.assertEqual(dest, self.npda.initial_state)
        self.assertTrue(source not in self.npda.states)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_read_input_machine_only(self) -> None:
        """Should construct the diagram with machine only for a NPDA reading input."""
        input_strings = ["abba", "aabbaa", "aabaabaa", ""]

        for input_string in input_strings:
            graph = self.npda.show_diagram(input_str=input_string, with_stack=False)
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            edge_pairs = [
                (edge[0].state, edge[1].state)
                for edge in self.npda._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_read_input_stack_only(self) -> None:
        """Should construct the diagram with stack only for a NPDA reading input."""
        input_strings = ["abba", "aabbaa", "aabaabaa", ""]

        for input_string in input_strings:
            graph = self.npda.show_diagram(input_str=input_string, with_machine=False)
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            input_path = self.npda._get_input_path(input_string)[0]
            edge_pairs = [(str(edge[0]), str(edge[1])) for edge in input_path]
            nodes = [node.attr["label"] for node in graph.nodes()]
            stack_content = [
                " | " + " | ".join(reversed(edge[0].stack)) for edge in input_path
            ] + [" | " + " | ".join(reversed(input_path[-1][1].stack))]

            self.assertEqual(nodes, stack_content)
            self.assertEqual(edge_pairs, colored_edges)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_write_file(self) -> None:
        """Should construct the diagram for a NPDA
        and write it to the specified file."""
        diagram_path = os.path.join(self.temp_dir_path, "test_npda.png")
        with contextlib.suppress(FileNotFoundError):
            os.remove(diagram_path)
        self.assertFalse(os.path.exists(diagram_path))
        self.npda.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_orientations(self) -> None:
        graph = self.npda.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")

        graph = self.npda.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")

        graph = self.npda.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")

        graph = self.npda.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram_fig_size(self) -> None:
        """Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering)."""
        graph = self.npda.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.npda.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")
