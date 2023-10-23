#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DPDAs."""

import os

from frozendict import frozendict

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.dpda import DPDA
from automata.pda.stack import PDAStack


class TestDPDA(test_pda.TestPDA):
    """A test class for testing deterministic finite automata."""

    def test_init_dpda(self) -> None:
        """Should copy DPDA if passed into DPDA constructor."""
        new_dpda = self.dpda.copy()
        self.assertIsNot(new_dpda, self.dpda)

    def test_init_dpda_missing_formal_params(self) -> None:
        """Should raise an error if formal DPDA parameters are missing."""
        with self.assertRaises(TypeError):
            DPDA(  # type: ignore
                states={"q0", "q1", "q2"},
                input_symbols={"a", "b"},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_init_dpda_no_acceptance_mode(self) -> None:
        """Should create a new DPDA."""
        new_dpda = DPDA(
            states={"q0"},
            input_symbols={"a", "b"},
            stack_symbols={"#"},
            transitions={"q0": {"a": {"#": ("q0", "")}}},
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q0"},
        )
        self.assertEqual(new_dpda.acceptance_mode, "both")

    def test_init_dpda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with self.assertRaises(pda_exceptions.InvalidAcceptanceModeError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
                acceptance_mode="foo",  # type: ignore
            )

    def test_dpda_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.dpda.states = set()

    def test_dpda_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.dpda.states

    def test_dpda_immutable_dict(self) -> None:
        """Should create a DPDA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.dpda.input_parameters)), int)

    def test_validate_invalid_input_symbol(self) -> None:
        """Should raise error if a transition has an invalid input symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {
                        "a": {"1": ("q1", ("1", "1"))},
                        "b": {"1": ("q2", "")},
                        "c": {"1": ("q2", "")},
                    },
                    "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_invalid_stack_symbol(self) -> None:
        """Should raise error if a transition has an invalid stack symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {
                        "a": {"1": ("q1", ("1", "1")), "2": ("q1", ("1", "1"))},
                        "b": {"1": ("q2", "")},
                    },
                    "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_nondeterminism(self) -> None:
        """Should raise error if DPDA exhibits nondeterminism."""
        with self.assertRaises(pda_exceptions.NondeterminismError):
            DPDA(
                states={"q0", "q1", "q2", "q3"},
                input_symbols={"a", "b"},
                stack_symbols={"0", "1"},
                transitions={
                    "q0": {"a": {"0": ("q1", ("1", "0"))}},
                    "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                    "q2": {
                        "b": {"0": ("q2", "0"), "1": ("q2", "")},
                        "": {"0": ("q3", ("0",))},
                    },
                },
                initial_state="q0",
                initial_stack_symbol="0",
                final_states={"q3"},
                acceptance_mode="final_state",
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q1",
                initial_stack_symbol="#",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_stack_symbol(self) -> None:
        """Should raise error if the initial stack symbol is invalid."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="2",
                final_states={"q0"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            DPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": ("q0", "")}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={1},
            )

    def test_read_input_valid_accept_by_final_state(self) -> None:
        """Should return correct config if DPDA accepts by final state."""
        self.assertEqual(
            self.dpda.read_input("aabb"), PDAConfiguration("q3", "", PDAStack(["0"]))
        )

    def test_read_input_invalid_accept_by_final_state(self) -> None:
        """Should not accept by final state if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="empty_stack",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aabb")

    def test_read_input_valid_accept_by_empty_stack(self) -> None:
        """Should return correct config if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="empty_stack",
        )
        self.assertEqual(
            dpda.read_input("aabb"), PDAConfiguration("q2", "", PDAStack([]))
        )

    def test_read_input_invalid_accept_by_empty_stack(self) -> None:
        """Should not accept by empty stack if DPDA accepts by final state."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aabb")

    def test_read_input_valid_consecutive_lambda_transitions(self) -> None:
        """Should follow consecutive lambda transitions when validating."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3", "q4"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q3", ("0",))}},
                "q3": {"": {"0": ("q4", ("0",))}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q4"},
            acceptance_mode="final_state",
        )
        self.assertEqual(
            dpda.read_input("aabb"), PDAConfiguration("q4", "", PDAStack(["0"]))
        )

    def test_read_input_rejected_accept_by_final_state(self) -> None:
        """Should reject strings if DPDA accepts by final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input("aab")

    def test_read_input_rejected_accept_by_empty_stack(self) -> None:
        """Should reject strings if DPDA accepts by empty stack."""
        dpda = DPDA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            stack_symbols={"0", "1"},
            transitions={
                "q0": {"a": {"0": ("q1", ("1", "0"))}},
                "q1": {"a": {"1": ("q1", ("1", "1"))}, "b": {"1": ("q2", "")}},
                "q2": {"b": {"1": ("q2", "")}, "": {"0": ("q2", "")}},
            },
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q3"},
            acceptance_mode="final_state",
        )
        with self.assertRaises(exceptions.RejectionException):
            dpda.read_input("aab")

    def test_read_input_rejected_undefined_transition(self) -> None:
        """Should reject strings which lead to an undefined transition."""
        with self.assertRaises(exceptions.RejectionException):
            self.dpda.read_input("01")

    def test_accepts_input_true(self) -> None:
        """Should return False if DPDA input is not accepted."""
        self.assertTrue(self.dpda.accepts_input("aabb"))

    def test_accepts_input_false(self) -> None:
        """Should return False if DPDA input is rejected."""
        self.assertFalse(self.dpda.accepts_input("aab"))

    def test_empty_dpda(self) -> None:
        """Should accept an empty input if the DPDA is empty."""
        dpda = DPDA(
            states={"q0"},
            input_symbols=set(),
            stack_symbols={"0"},
            transitions=dict(),
            initial_state="q0",
            initial_stack_symbol="0",
            final_states={"q0"},
            acceptance_mode="both",
        )
        self.assertTrue(dpda.accepts_input(""))

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

        self.assertRaises(
            exceptions.DiagramException,
            self.dpda.show_diagram,
            "ab",
            with_machine=False,
            with_stack=False,
        )

    def test_show_diagram_read_input_machine_only(self) -> None:
        """
        Should construct the diagram with machine only for a DPDA reading input.
        """
        input_strings = ["ab", "aabb", "aaabbb"]

        for input_string in input_strings:
            graph = self.dpda.show_diagram(input_str=input_string, with_stack=False)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]

            edge_pairs = [
                (edge[0].state, edge[1].state)
                for edge in self.dpda._get_input_path(input_string)[0]
            ]
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_read_input_stack_only(self) -> None:
        """
        Should construct the diagram with stack only for a DPDA reading input.
        """
        input_strings = ["ab", "aabb", "aaabbb"]

        for input_string in input_strings:
            graph = self.dpda.show_diagram(input_str=input_string, with_machine=False)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]

            edge_pairs = [
                (str(edge[0]), str(edge[1]))
                for edge in self.dpda._get_input_path(input_string)[0]
            ]

            # Get stack content corresponding to input path
            nodes = [node.attr["label"] for node in graph.nodes()]

            stack_content = [
                " | " + " | ".join(reversed(edge.stack))
                for edge in list(self.dpda.read_input_stepwise(input_string))
            ]

            self.assertEqual(nodes, stack_content)
            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a DPDA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, "test_dpda.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
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
        """
        Testing figure size. Just need to make sure it matches the input
        (the library handles the rendering).
        """
        graph = self.dpda.show_diagram(fig_size=(1.1, 2))
        self.assertEqual(graph.graph_attr["size"], "1.1, 2")

        graph = self.dpda.show_diagram(fig_size=(3.3,))
        self.assertEqual(graph.graph_attr["size"], "3.3")
