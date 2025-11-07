"""Diagram rendering tests for generalized NFAs."""

import os
import unittest

from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_gnfa.base import GNFATestCase


class TestGNFAVisualization(GNFATestCase):
    """Exercise diagram generation and persistence utilities."""

    @unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
    def test_show_diagram(self) -> None:
        """Should construct the diagram for a GNFA."""
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
        """Should construct the diagram for a GNFA and write it to file."""
        diagram_path = os.path.join(self.temp_dir_path, "test_gnfa.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.gnfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)
