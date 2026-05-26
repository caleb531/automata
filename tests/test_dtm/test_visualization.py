"""Visualization-centric DTM tests."""

import contextlib
import os
import tempfile
import unittest

from tests.optional import VISUAL_OK, VISUAL_SKIP_REASON
from tests.test_tm import TestTM


@unittest.skipIf(not VISUAL_OK, VISUAL_SKIP_REASON)
class TestDTMVisualization(TestTM):
    """Ensure DTM diagram generation remains stable."""

    temp_dir_path = tempfile.gettempdir()

    def test_show_diagram_1(self) -> None:
        """Should construct the diagram for a DTM."""
        dtm = self.dtm1
        graph = dtm.show_diagram()
        node_names = {node.get_name() for node in graph.nodes()}
        self.assertTrue(set(dtm.states).issubset(node_names))
        self.assertEqual(len(dtm.states) + 1, len(node_names))

        for state in dtm.states:
            node = graph.get_node(state)
            expected_shape = (
                "doublecircle" if state in dtm.final_states else "circle"
            )
            self.assertEqual(node.attr["shape"], expected_shape)

        edge_formatter = dtm._get_edge_name
        expected_transitions = {
            ("q0", edge_formatter("0", "x", "R"), "q1"),
            ("q0", edge_formatter("y", "y", "R"), "q3"),

            ("q1", ",".join([
                edge_formatter("0", "0", "R"),
                edge_formatter("y","y","R")]), "q1"),
            ("q1", edge_formatter("1", "y", "L"), "q2"),

            ("q2", ",".join([
                edge_formatter("0", "0", "L"),
                edge_formatter("y","y","L")]), "q2"),
            ("q2", edge_formatter("x", "x", "R"), "q0"),

            ("q3", edge_formatter("y", "y", "R"), "q3"),
            ("q3", edge_formatter(".", ".", "R"), "q4"),
        }
        seen_transitions = {
            (edge[0], edge.attr["label"], edge[1]) for edge in graph.edges()
        }
        self.assertTrue(expected_transitions.issubset(seen_transitions))
        self.assertEqual(len(expected_transitions) + 1, len(seen_transitions))

        source, symbol, dest = list(seen_transitions - expected_transitions)[0]
        self.assertEqual(symbol, "")
        self.assertEqual(dest, dtm.initial_state)
        self.assertTrue(source not in dtm.states)


    def test_show_diagram_write_file(self) -> None:
        """Should construct the diagram for a DTM
        and write it to the specified file."""
        diagram_path = os.path.join(self.temp_dir_path, "test_dtm.png")
        with contextlib.suppress(FileNotFoundError):
            os.remove(diagram_path)
        self.assertFalse(os.path.exists(diagram_path))
        self.dtm1.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_show_diagram_orientations(self) -> None:
        graph = self.dtm1.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")
        graph = self.dtm1.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")
        graph = self.dtm1.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")
        graph = self.dtm1.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_fig_size(self) -> None:
        """Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering)."""
        graph = self.dtm1.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.dtm1.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")

    def test_show_diagram_special_characters_in_state_names(self) -> None:
        """Should handle state names with special characters (issue #268)."""
        from automata.tm.dtm import DTM

        dtm = DTM(
            states={
                "%a=0",
                'state%"q',
                "state%\\path",
                "state{brace}",
                "state[bracket]",
                "state<angle>",
                "state|pipe",
                "state:colon",
                "state;semi",
                "state,comma",
                "state space",
                "normal",
            },
            input_symbols={"0", "1"},
            tape_symbols={"0", "1", "."},
            transitions = {
                "%a=0": {
                    "0": ('state%"q', "0", "R"),
                    "1": ("state%\\path", "1", "R"),
                },

                'state%"q': {
                    "0": ("state{brace}", "0", "R"),
                    "1": ("state[bracket]", "1", "R"),
                },

                "state%\\path": {
                    "0": ("state<angle>", "0", "R"),
                    "1": ("state|pipe", "1", "R"),
                },

                "state{brace}": {
                    "0": ("state:colon", "0", "R"),
                    "1": ("state;semi", "1", "R"),
                },

                "state[bracket]": {
                    "0": ("state,comma", "0", "R"),
                    "1": ("state space", "1", "R"),
                },

                "state<angle>": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                },

                "state|pipe": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                },

                "state:colon": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                },

                "state;semi": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                },

                "state,comma": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                },

                "state space": {
                    "0": ("normal", "0", "R"),
                    "1": ("normal", "1", "R"),
                }
            },
            blank_symbol=".",
            initial_state="%a=0",
            final_states={"normal"},
        )

        # This should not raise an error
        graph = dtm.show_diagram()

        # Verify the graph was created successfully
        node_names = {node.get_name() for node in graph.nodes()}

        # States with special DOT characters replaced with Unicode equivalents
        self.assertIn("\ufe6aa=0", node_names)  # % → ﹪ (U+FE6A)
        self.assertIn('state\ufe6a"q', node_names)  # % → ﹪
        self.assertIn("state\ufe6a\\path", node_names)  # % → ﹪
        self.assertIn("state\u2774brace\u2775", node_names)  # {} → ❴❵
        self.assertIn(
            "state\uff3bbracket\uff3d", node_names
        )  # [] → ［］ (U+FF3B, U+FF3D)
        self.assertIn(
            "state\ufe64angle\ufe65", node_names
        )  # <> → ﹤﹥ (U+FE64, U+FE65)
        self.assertIn("state\uff5cpipe", node_names)  # | → ｜ (U+FF5C)

        # Characters not in the replacement list remain unchanged
        self.assertIn("state:colon", node_names)
        self.assertIn("state;semi", node_names)
        self.assertIn("state,comma", node_names)
        self.assertIn("state space", node_names)
        self.assertIn("normal", node_names)
