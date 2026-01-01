"""Visualization-centric DFA tests."""

import contextlib
import os
import random
import unittest

from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_dfa.base import DFATestCase


@unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
class TestDFAVisualization(DFATestCase):
    """Ensure DFA diagram generation remains stable."""

    def test_show_diagram_initial_final_different(self) -> None:
        """Should construct the diagram for a DFA whose initial state
        is not a final state."""
        graph = self.dfa.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(self.dfa.states).issubset(node_names))
        self.assertEqual(len(self.dfa.states) + 1, len(node_names))

        for state in self.dfa.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in self.dfa.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("q0", "0", "q0"),
            ("q0", "1", "q1"),
            ("q1", "0", "q0"),
            ("q1", "1", "q2"),
            ("q2", "0", "q2"),
            ("q2", "1", "q1"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, self.dfa.initial_state)
        self.assertTrue(source not in self.dfa.states)

    def test_show_diagram_read_input(self) -> None:
        """Should construct the diagram for a DFA reading input."""
        input_strings = ["0111", "001", "01110011", "001011001", "1100", ""]

        for input_string in input_strings:
            graph = self.dfa.show_diagram(input_str=input_string)

            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            colored_edges.sort(key=lambda edge: edge.attr["label"][2:])

            edge_pairs = [
                edge[0:2] for edge in self.dfa._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_initial_final_same(self) -> None:
        """Should construct the diagram for a DFA whose initial state
        is also a final state."""
        dfa = self.no_consecutive_11_dfa

        graph = dfa.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(dfa.states).issubset(node_names))
        self.assertEqual(len(dfa.states) + 1, len(node_names))

        for state in dfa.states:
            node = graph.get_node(state)
            expected_shape = "doublecircle" if state in dfa.final_states else "circle"
            self.assertEqual(node.attr["shape"], expected_shape)

        expected_transitions = {
            ("p0", "0", "p0"),
            ("p0", "1", "p1"),
            ("p1", "0", "p0"),
            ("p1", "1", "p2"),
            ("p2", "0,1", "p2"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, dfa.initial_state)
        self.assertTrue(source not in dfa.states)

    def test_show_diagram_write_file(self) -> None:
        """Should construct the diagram for a DFA
        and write it to the specified file."""
        diagram_path = os.path.join(self.temp_dir_path, "test_dfa.png")
        with contextlib.suppress(FileNotFoundError):
            os.remove(diagram_path)
        self.assertFalse(os.path.exists(diagram_path))
        self.dfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_repr_mimebundle_same(self) -> None:
        """Check that the mimebundle is the same."""
        random.seed(42)
        first_repr = self.dfa._repr_mimebundle_()
        random.seed(42)
        second_repr = self.dfa.show_diagram()._repr_mimebundle_()
        self.assertEqual(first_repr, second_repr)

    def test_show_diagram_orientations(self) -> None:
        graph = self.dfa.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")
        graph = self.dfa.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")
        graph = self.dfa.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")
        graph = self.dfa.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_fig_size(self) -> None:
        """Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering)."""
        graph = self.dfa.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.dfa.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")

    def test_show_diagram_percent_in_state_name(self) -> None:
        """Should handle state names containing % character (issue #268)."""
        from automata.fa.dfa import DFA

        dfa = DFA(
            states={"%a=0", "q1", "q2"},
            input_symbols={"0", "1"},
            transitions={
                "%a=0": {"0": "q1", "1": "q2"},
                "q1": {"0": "q1", "1": "q2"},
                "q2": {"0": "q2", "1": "q2"},
            },
            initial_state="%a=0",
            final_states={"q2"},
        )

        # This should not raise an error
        graph = dfa.show_diagram()

        # Verify the graph was created successfully
        node_names = {node.get_name() for node in graph.nodes()}
        # State names with % should be replaced with fullwidth percent sign (\uff05)
        self.assertIn("\uff05a=0", node_names)
        self.assertIn("q1", node_names)
        self.assertIn("q2", node_names)
