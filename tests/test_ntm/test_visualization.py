"""Visualization-centric NTM tests."""

import unittest

from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_tm import TestTM


@unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
class TestNTMVisualization(TestTM):
    """Ensure DTM diagram generation remains stable."""

    def test_show_diagram_1(self) -> None:
        """Should construct the diagram for a DTM."""
        ntm = self.ntm1
        graph = ntm.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(ntm.states).issubset(node_names))
        self.assertEqual(len(ntm.states) + 1, len(node_names))

        for state in ntm.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in ntm.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        edge_formatter = ntm._get_edge_name
        expected_transitions = {
            ("q0", edge_formatter("0", "0", "R"), "q0"),
            ("q0", edge_formatter("1", "1", "R"), "q1"),
            ("q0", edge_formatter("1", "1", "R"), "q2"),

            ("q1", edge_formatter("1", "1", "R"), "q1"),
            ("q1", edge_formatter(".", ".", "N"), "q3"),

            ("q2", edge_formatter("2", "2", "R"), "q0")
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, ntm.initial_state)
        self.assertTrue(source not in ntm.states)
