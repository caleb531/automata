"""Classes and functions for testing the behavior of NPDAs."""

import os

from frozendict import frozendict

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.npda import NPDA
from automata.pda.stack import PDAStack


class TestNPDA(test_pda.TestPDA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_npda(self) -> None:
        """Should copy NPDA if passed into NPDA constructor."""
        new_npda = self.npda.copy()
        self.assertIsNot(new_npda, self.npda)

    def test_init_npda_missing_formal_params(self) -> None:
        """Should raise an error if formal NPDA parameters are missing."""
        with self.assertRaises(TypeError):
            NPDA(  # type: ignore
                states={"q0", "q1", "q2"},
                input_symbols={"a", "b"},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_init_npda_no_acceptance_mode(self) -> None:
        """Should create a new NPDA."""
        new_npda = NPDA(
            states={"q0"},
            input_symbols={"a", "b"},
            stack_symbols={"#"},
            transitions={
                "q0": {
                    "a": {"#": {("q0", "")}},
                }
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q0"},
        )
        self.assertEqual(new_npda.acceptance_mode, "both")

    def test_init_npda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with self.assertRaises(pda_exceptions.InvalidAcceptanceModeError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
                acceptance_mode="foo",  # type: ignore
            )

    def test_npda_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.npda.states = set()

    def test_npda_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.npda.states

    def test_npda_immutable_dict(self) -> None:
        """Should create an NPDA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.npda.input_parameters)), int)

    def test_validate_invalid_input_symbol(self) -> None:
        """Should raise error if a transition has an invalid input symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"c": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"@": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="@",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={1},
            )

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if NPDA accepts by final state."""
        self.assertEqual(
            self.npda.read_input("abaaba"),
            {PDAConfiguration("q2", "", PDAStack(["#"]))},
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q2"},
            acceptance_mode="empty_stack",
        )
        with self.assertRaises(exceptions.RejectionException):
            (npda.read_input("abaaba"),)

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q2", "")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states=set(),
            acceptance_mode="empty_stack",
        )
        self.assertEqual(
            npda.read_input("abaaba"), {PDAConfiguration("q2", "", PDAStack([]))}
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if NPDA accepts by final state."""
        npda = NPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q3", "")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q2"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            npda.read_input("abaaba")

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        npda = NPDA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q3", "#")}}},
                "q3": {"": {"#": {("q4", "#")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q4"},
            acceptance_mode="final_state",
        )
        self.assertEqual(
            npda.read_input("abaaba"), {PDAConfiguration("q4", "", PDAStack(["#"]))}
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if NPDA accepts by final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.npda.read_input("aaba")

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if NPDA accepts by empty stack."""
        npda = NPDA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            stack_symbols={"A", "B", "#"},
            transitions={
                "q0": {
                    "": {
                        "#": {("q2", "#")},
                    },
                    "a": {
                        "#": {("q0", ("A", "#"))},
                        "A": {
                            ("q0", ("A", "A")),
                            ("q1", ""),
                        },
                        "B": {("q0", ("A", "B"))},
                    },
                    "b": {
                        "#": {("q0", ("B", "#"))},
                        "A": {("q0", ("B", "A"))},
                        "B": {
                            ("q0", ("B", "B")),
                            ("q1", ""),
                        },
                    },
                },
                "q1": {
                    "": {"#": {("q2", "#")}},
                    "a": {"A": {("q1", "")}},
                    "b": {"B": {("q1", "")}},
                },
                "q2": {"": {"#": {("q2", "")}}},
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states=set(),
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            npda.read_input("aaba")

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with self.assertRaises(exceptions.RejectionException):
            self.npda.read_input("01")

    def test_accepts_input_true(self) -> None:
        """Should return True if NPDA input is accepted."""
        self.assertTrue(self.npda.accepts_input("abaaba"))

    def test_accepts_input_false(self) -> None:
        """Should return False if NPDA input is rejected."""
        self.assertFalse(self.npda.accepts_input("aaba"))

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

    def test_show_diagram_read_input_machine_only(self) -> None:
        """
        Should construct the diagram with machine only for a NPDA reading input.
        """
        input_strings = ["abba", "aabbaa", "aabaabaa", ""]

        for input_string in input_strings:
            graph = self.npda.show_diagram(input_str=input_string, with_stack=False)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]

            edge_pairs = [
                (edge[0].state, edge[1].state)
                for edge in self.npda._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_read_input_stack_only(self) -> None:
        """
        Should construct the diagram with stack only for a NPDA reading input.
        """
        input_strings = ["abba", "aabbaa", "aabaabaa", ""]

        for input_string in input_strings:
            graph = self.npda.show_diagram(input_str=input_string, with_machine=False)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]

            input_path = self.npda._get_input_path(input_string)[0]

            edge_pairs = [(str(edge[0]), str(edge[1])) for edge in input_path]

            # Get stack content corresponding to input path
            nodes = [node.attr["label"] for node in graph.nodes()]

            stack_content = [
                " | " + " | ".join(reversed(edge[0].stack)) for edge in input_path
            ] + [" | " + " | ".join(reversed(input_path[-1][1].stack))]

            self.assertEqual(nodes, stack_content)
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a NPDA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, "test_npda.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.npda.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_show_diagram_orientations(self) -> None:
        graph = self.npda.show_diagram()
        self.assertEqual(graph.graph_attr["rankdir"], "LR")
        graph = self.npda.show_diagram(horizontal=False)
        self.assertEqual(graph.graph_attr["rankdir"], "TB")
        graph = self.npda.show_diagram(reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "RL")
        graph = self.npda.show_diagram(horizontal=False, reverse_orientation=True)
        self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_fig_size(self) -> None:
        """
        Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering).
        """
        graph = self.npda.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.npda.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")
