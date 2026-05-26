"""Diagram rendering and tracing tests for deterministic pushdown automata."""

import contextlib
import os
import unittest

import automata.base.exceptions as exceptions
from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_dpda.base import DPDATestCase


@unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
class TestDPDAVisualization(DPDATestCase):
    """Exercise diagram generation and path-highlighting helpers."""

    def test_show_diagram(self) -> None:
        """Should construct the diagram for a DPDA"""
        graph = self.dpda.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.dpda.states).issubset(node_names))
        self.assertEqual(len(self.dpda.states) + 1, len(node_names))

        for state in self.dpda.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.dpda.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", "a, 0 | 10", "q1"),
            ("q1", "a, 1 | 11", "q1"),
            ("q1", "b, 1 | ε", "q2"),
            ("q2", "b, 1 | ε", "q2"),
            ("q2", "ε, 0 | 0", "q3"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, self.dpda.initial_state)
        self.assertTrue(source not in self.dpda.states)

    def test_show_diagram_exception(self) -> None:
        """Should raise exception"""
        with self.assertRaises(exceptions.DiagramException):
            self.dpda.show_diagram("ab", with_machine=False, with_stack=False)

    def test_show_diagram_read_input_machine_only(self) -> None:
        """Should construct the diagram with machine only for a DPDA reading input."""
        input_strings = ["ab", "aabb", "aaabbb"]

        for input_string in input_strings:
            graph = self.dpda.show_diagram(input_str=input_string, with_stack=False)
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            edge_pairs = [
                (edge[0].state, edge[1].state)
                for edge in self.dpda._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_read_input_stack_only(self) -> None:
        """Should construct the diagram with stack only for a DPDA reading input."""
        input_strings = ["ab", "aabb", "aaabbb"]

        for input_string in input_strings:
            graph = self.dpda.show_diagram(input_str=input_string, with_machine=False)
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            edge_pairs = [
                (str(edge[0]), str(edge[1]))
                for edge in self.dpda._get_input_path(input_string)[0]
            ]
            nodes = [node.attr["label"] for node in graph.nodes()]
            stack_content = [
                " | " + " | ".join(reversed(edge.stack))
                for edge in list(self.dpda.read_input_stepwise(input_string))
            ]
            self.assertEqual(nodes, stack_content)
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_write_file(self) -> None:
        """Should construct the diagram for a DPDA
        and write it to the specified file."""
        diagram_path = os.path.join(self.temp_dir_path, "test_dpda.png")
        with contextlib.suppress(FileNotFoundError):
            os.remove(diagram_path)
        self.assertFalse(os.path.exists(diagram_path))
        self.dpda.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_show_diagram_orientations(self) -> None:
        graph = self.dpda.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")

        graph = self.dpda.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")

        graph = self.dpda.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")

        graph = self.dpda.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_fig_size(self) -> None:
        """Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering)."""
        graph = self.dpda.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.dpda.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")
