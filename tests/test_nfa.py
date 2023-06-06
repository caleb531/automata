#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""
import os
import random
import string
import tempfile
import types
from itertools import product
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_nfa(self) -> None:
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self) -> None:
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            NFA(  # type: ignore
                states={"q0", "q1"},
                input_symbols={"0", "1"},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_copy_nfa(self) -> None:
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_nfa_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.nfa.states = {}  # type: ignore

    def test_nfa_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.nfa.states

    def test_nfa_immutable_dict(self) -> None:
        """Should create an NFA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.nfa.input_parameters)), int)

    def test_init_dfa(self) -> None:
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA.from_dfa(self.dfa)
        self.assertEqual(nfa.states, {"q0", "q1", "q2"})
        self.assertEqual(nfa.input_symbols, {"0", "1"})
        self.assertEqual(
            nfa.transitions,
            {
                "q0": {"0": {"q0"}, "1": {"q1"}},
                "q1": {"0": {"q0"}, "1": {"q2"}},
                "q2": {"0": {"q2"}, "1": {"q1"}},
            },
        )
        self.assertEqual(nfa.initial_state, "q0")

    @patch("automata.fa.nfa.NFA.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate NFA when initialized."""
        self.nfa.copy()
        validate.assert_called_once_with()

    def test_nfa_equal(self) -> None:
        """Should correctly determine if two NFAs are equal."""
        nfa1 = NFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"": {"q1"}},
                "q1": {"a": {"q2"}},
                "q2": {"a": {"q2"}, "": {"q3"}},
                "q3": {"b": {"q1"}},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        nfa2 = NFA(
            states={0, 1, 2, 3},
            input_symbols={"a", "b"},
            transitions={
                0: {"": {1}},
                1: {"a": {2}},
                2: {"a": {2}, "": {3}},
                3: {"b": {1}},
            },
            initial_state=0,
            final_states={3},
        )
        self.assertEqual(nfa1, nfa2)
        self.assertEqual(nfa1.eliminate_lambda(), nfa2.eliminate_lambda())

    def test_nfa_not_equal(self) -> None:
        """Should correctly determine if two NFAs are not equal."""
        nfa1 = NFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": {"q1"}},
                "q1": {"a": {"q1"}, "": {"q2"}},
                "q2": {"b": {"q0"}},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        nfa2 = NFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": {"q0"}}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertNotEqual(nfa1, nfa2)

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"b": {"q0"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q1"}}},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q1",
                final_states={"q0"},
            )

    def test_validate_initial_state_transitions(self) -> None:
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            NFA(
                states={"q0", "q1"},
                input_symbols={"a"},
                transitions={},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q0",
                final_states={"q1"},
            )

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={"q0"},
                input_symbols={"a"},
                transitions={"q0": {"a": {"q0"}}},
                initial_state="q0",
                final_states={3},
            )
            self.nfa.validate()

    def test_read_input_accepted(self) -> None:
        """Should return correct states if acceptable NFA input is given."""
        self.assertEqual(self.nfa.read_input("aba"), {"q1", "q2"})

    def test_validate_missing_state(self) -> None:
        """Should silently ignore states without transitions defined."""
        NFA(
            states={"q0"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": {"q0"}}},
            initial_state="q0",
            final_states={"q0"},
        )
        self.assertIsNotNone(self.nfa.transitions)

    def test_read_input_rejection(self) -> None:
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abba")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input("abc")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise("aba")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(
            list(validation_generator), [{"q0"}, {"q1", "q2"}, {"q0"}, {"q1", "q2"}]
        )

    def test_accepts_input_true(self) -> None:
        """Should return True if NFA input is accepted."""
        self.assertTrue(self.nfa.accepts_input("aba"))

    def test_accepts_input_false(self) -> None:
        """Should return False if NFA input is rejected."""
        self.assertFalse(self.nfa.accepts_input("abba"))

    def test_cyclic_lambda_transitions(self) -> None:
        """Should traverse NFA containing cyclic lambda transitions."""
        # NFA which matches zero or more occurrences of 'a'
        nfa = NFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"a"},
            transitions={
                "q0": {"": {"q1", "q3"}},
                "q1": {"a": {"q2"}},
                "q2": {"": {"q3"}},
                "q3": {"": {"q0"}},
            },
            initial_state="q0",
            final_states={"q3"},
        )
        self.assertEqual(nfa.read_input(""), {"q0", "q1", "q3"})
        self.assertEqual(nfa.read_input("a"), {"q0", "q1", "q2", "q3"})

    def test_non_str_states(self) -> None:
        """Should handle non-string state names"""
        nfa = NFA(
            states={0},
            input_symbols={"0"},
            transitions={0: {}},
            initial_state=0,
            final_states=set(),
        )
        # We don't care what the output is, just as long as no exception is
        # raised
        self.assertIsNotNone(nfa.accepts_input(""))

    def test_operations_other_type(self) -> None:
        """Should raise TypeError for concatenate."""
        nfa = NFA(
            states={"q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q1": {"0": {"q1"}, "1": {"q1", "q2"}},
                "q2": {"": {"q2"}, "0": {"q2"}},
                "q3": {"1": {"q4"}},
                "q4": {"0": {"q4"}, "1": {"q4"}},
            },
            initial_state="q1",
            final_states={"q2", "q4"},
        )
        other = 42
        with self.assertRaises(TypeError):
            nfa + other  # type: ignore

    def test_concatenate(self) -> None:
        nfa_a = NFA(
            states={"q1", "q2", "q3", "q4"},
            input_symbols={"0", "1"},
            transitions={
                "q1": {"0": {"q1"}, "1": {"q1", "q2"}},
                "q2": {"": {"q2"}, "0": {"q2"}},
                "q3": {"1": {"q4"}},
                "q4": {"0": {"q4"}, "1": {"q4"}},
            },
            initial_state="q1",
            final_states={"q2", "q4"},
        )

        nfa_b = NFA(
            states={"r1", "r2", "r3"},
            input_symbols={"0", "1"},
            transitions={
                "r1": {"": {"r3"}, "1": {"r2"}},
                "r2": {"0": {"r2", "r3"}, "1": {"r3"}},
                "r3": {"0": {"r1"}},
            },
            initial_state="r1",
            final_states={"r1"},
        )

        concat_nfa = nfa_a + nfa_b

        self.assertFalse(concat_nfa.accepts_input(""))
        self.assertFalse(concat_nfa.accepts_input("0"))
        self.assertTrue(concat_nfa.accepts_input("1"))
        self.assertFalse(concat_nfa.accepts_input("00"))
        self.assertTrue(concat_nfa.accepts_input("01"))
        self.assertTrue(concat_nfa.accepts_input("10"))
        self.assertTrue(concat_nfa.accepts_input("11"))
        self.assertTrue(concat_nfa.accepts_input("101"))
        self.assertTrue(concat_nfa.accepts_input("101100"))
        self.assertTrue(concat_nfa.accepts_input("1010"))

    def test_kleene_star(self) -> None:
        """Should perform the Kleene Star operation on an NFA"""
        # This NFA accepts aa and ab
        nfa = NFA(
            states={0, 1, 2, 3, 4, 6, 10},
            input_symbols={"a", "b"},
            transitions={
                0: {"a": {1, 3}},
                1: {"b": {2}},
                2: {},
                3: {"a": {4}},
                4: {"": {6}},
                6: {},
            },
            initial_state=0,
            final_states={2, 4, 6, 10},
        )
        # This NFA should then accept any number of repetitions
        # of aa or ab concatenated together.
        kleene_nfa = nfa.kleene_star()
        self.assertTrue(kleene_nfa.accepts_input(""))
        self.assertFalse(kleene_nfa.accepts_input("a"))
        self.assertFalse(kleene_nfa.accepts_input("b"))
        self.assertTrue(kleene_nfa.accepts_input("aa"))
        self.assertTrue(kleene_nfa.accepts_input("ab"))
        self.assertFalse(kleene_nfa.accepts_input("ba"))
        self.assertFalse(kleene_nfa.accepts_input("bb"))
        self.assertFalse(kleene_nfa.accepts_input("aaa"))
        self.assertFalse(kleene_nfa.accepts_input("aba"))
        self.assertTrue(kleene_nfa.accepts_input("abaa"))
        self.assertFalse(kleene_nfa.accepts_input("abba"))
        self.assertFalse(kleene_nfa.accepts_input("aaabababaaaaa"))
        self.assertTrue(kleene_nfa.accepts_input("aaabababaaaaab"))
        self.assertFalse(kleene_nfa.accepts_input("aaabababaaaaba"))

    def test_reverse(self) -> None:
        """Should reverse an NFA"""
        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={"a", "b"},
            transitions={
                0: {"a": {1}},
                1: {"a": {2}, "b": {1, 2}},
                2: {},
                3: {"a": {2}, "b": {2}},
            },
            initial_state=0,
            final_states={2},
        )

        reverse_nfa = nfa.reverse()
        self.assertFalse(reverse_nfa.accepts_input("a"))
        self.assertFalse(reverse_nfa.accepts_input("ab"))
        self.assertTrue(reverse_nfa.accepts_input("ba"))
        self.assertTrue(reverse_nfa.accepts_input("bba"))
        self.assertTrue(reverse_nfa.accepts_input("bbba"))

    def test_from_regex(self) -> None:
        """Test if from_regex produces correct NFA"""
        input_symbols = {"a", "b", "c", "d"}
        nfa1 = NFA.from_regex("ab(cd*|dc)|a?", input_symbols=input_symbols)
        nfa2 = NFA(
            states={0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
            input_symbols=input_symbols,
            initial_state=0,
            transitions={
                0: {"": {1, 10}},
                1: {"a": {2}},
                2: {"b": {3}},
                3: {"": {4, 7}},
                4: {"d": {5}},
                5: {"c": {6}},
                7: {"c": {8}},
                8: {"d": {9}},
                9: {"d": {9}},
                10: {"a": {11}},
            },
            final_states={6, 8, 9, 10, 11},
        )

        self.assertEqual(nfa1, nfa2)

    def test_from_regex_empty_string(self) -> None:
        NFA.from_regex("")

    def test_eliminate_lambda(self) -> None:
        original_nfa = NFA(
            states={0, 1, 2, 3, 4, 5, 6},
            initial_state=0,
            input_symbols={"a", "b", "c"},
            transitions={
                0: {"a": {1}},
                1: {"": {2, 6}, "b": {2}},
                2: {"": {4}, "c": {3}},
                4: {"a": {5}},
            },
            final_states={3, 6},
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)
        nfa2 = NFA(
            states={0, 1, 2, 3, 5},
            initial_state=0,
            input_symbols={"a", "b", "c"},
            transitions={
                0: {"a": {1}},
                1: {"a": {5}, "b": {2}, "c": {3}},
                2: {"a": {5}, "c": {3}},
            },
            final_states={1, 3},
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(nfa1._lambda_closures, original_nfa._lambda_closures)

    def test_eliminate_lambda_other(self) -> None:
        original_nfa = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={"a", "b"},
            transitions={0: {"a": {1}}, 1: {"": {2}, "b": {1}}, 2: {"b": {2}}},
            final_states={2},
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)

        nfa2 = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={"a", "b"},
            transitions={0: {"a": {1}}, 1: {"b": {1, 2}}, 2: {"b": {2}}},
            final_states={1, 2},
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(nfa1._lambda_closures, original_nfa._lambda_closures)

    def test_eliminate_lambda_regex(self) -> None:
        nfa = NFA.from_regex(
            "a(aaa*bbcd|abbcd)d*|aa*bb(dcc*|(d|c)b|a?bb(dcc*|(d|c)))ab(c|d)*(ccd)?"
        )
        nfa_without_lambdas = nfa.eliminate_lambda()
        self.assertEqual(nfa, nfa_without_lambdas)

        for transition in nfa_without_lambdas.transitions.values():
            for char in transition.keys():
                self.assertNotEqual(char, "")

    def test_option(self) -> None:
        """
        Given a NFA recognizing language L, should return NFA
        such that it accepts the language 'L?'
        that zero or one occurrence of L.
        """
        nfa1 = NFA.from_regex("a*b")
        nfa1 = nfa1.option()
        self.assertTrue(nfa1.accepts_input("aab"))
        self.assertTrue(
            nfa1.initial_state in nfa1.final_states
            and nfa1.initial_state
            not in sum(
                [
                    list(nfa1.transitions[state].values())
                    for state in nfa1.transitions.keys()
                ],
                [],
            )
        )

    def test_union(self) -> None:
        input_symbols = {"a", "b"}
        nfa1 = NFA.from_regex("ab*", input_symbols=input_symbols)
        nfa2 = NFA.from_regex("ba*", input_symbols=input_symbols)

        nfa3 = nfa1.union(nfa2)

        nfa4 = NFA(
            states={0, 1, 2, 3, 4},
            input_symbols=input_symbols,
            transitions={
                0: {"": {1, 3}},
                2: {"b": {2}},
                1: {"a": {2}},
                3: {"b": {4}},
                4: {"a": {4}},
            },
            final_states={2, 4},
            initial_state=0,
        )

        self.assertEqual(nfa3, nfa4)

        # second check
        nfa5 = nfa1 | nfa2
        self.assertEqual(nfa5, nfa4)

        # third check: union of NFA which is subset of other
        nfa6 = NFA.from_regex("aa*")
        nfa7 = NFA.from_regex("a*")
        nfa8 = nfa6.union(nfa7)
        nfa9 = nfa7.union(nfa6)
        self.assertEqual(nfa8, nfa7)
        self.assertEqual(nfa9, nfa7)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa | self.dfa  # type: ignore

    def test_intersection(self) -> None:
        nfa1 = NFA.from_regex("aaaa*")
        nfa2 = NFA.from_regex("(a)|(aa)|(aaa)")

        nfa3 = nfa1.intersection(nfa2)

        nfa4 = NFA.from_regex("aaa")
        self.assertEqual(nfa3, nfa4)
        # second check
        nfa5 = nfa1 & nfa2

        self.assertEqual(nfa5, nfa4)

        # third check: intersection of NFA which is subset of other
        nfa6 = NFA.from_regex("aa*")
        nfa7 = NFA.from_regex("a*")
        nfa8 = nfa6.intersection(nfa7)
        nfa9 = nfa7.intersection(nfa6)
        self.assertEqual(nfa8, nfa6)
        self.assertEqual(nfa9, nfa6)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa & self.dfa  # type: ignore

    def test_validate_regex(self) -> None:
        """Should raise an error if invalid regex is passed into NFA.from_regex()"""

        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "ab|")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "?")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a|b|*")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a||b")
        self.assertRaises(
            exceptions.InvalidRegexError, NFA.from_regex, "((abc*)))((abd)"
        )
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "*")
        self.assertRaises(
            exceptions.InvalidRegexError, NFA.from_regex, "ab(bc)*((bbcd)"
        )
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a(*)")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "ab(|)")

    def test_show_diagram_initial_final_same(self) -> None:
        """
        Should construct the diagram for a NFA whose initial state
        is also a final state.
        """

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

    def test_show_diagram_orientations(self) -> None:
        for automaton in [self.nfa, self.dfa]:
            graph = automaton.show_diagram()
            self.assertEqual(graph.graph_attr["rankdir"], "LR")
            graph = automaton.show_diagram(horizontal=False)
            self.assertEqual(graph.graph_attr["rankdir"], "TB")
            graph = automaton.show_diagram(reverse_orientation=True)
            self.assertEqual(graph.graph_attr["rankdir"], "RL")
            graph = automaton.show_diagram(horizontal=False, reverse_orientation=True)
            self.assertEqual(graph.graph_attr["rankdir"], "BT")

    def test_show_diagram_read_input(self) -> None:
        """
        Should construct the diagram for a NFA reading input.
        """
        input_strings = ["ababa", "bba", "aabba", "baaab", "bbaab", ""]

        for input_string in input_strings:
            graph = self.nfa.show_diagram(input_str=input_string)

            # Get edges corresponding to input path
            colored_edges = [
                edge for edge in graph.edges() if "color" in dict(edge.attr)
            ]
            colored_edges.sort(key=lambda edge: edge.attr["label"][2:])

            edge_pairs = [
                edge[0:2] for edge in self.nfa._get_input_path(input_string)[0]
            ]

            self.assertEqual(edge_pairs, colored_edges)

    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a NFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, "test_dfa.png")
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.nfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_repr_mimebundle_same(self) -> None:
        """
        Should construct the diagram for a NFA whose initial state
        is also a final state.
        """

        random.seed(42)
        first_repr = self.nfa._repr_mimebundle_()
        random.seed(42)
        second_repr = self.nfa.show_diagram()._repr_mimebundle_()
        self.assertEqual(first_repr, second_repr)

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
        """A test case for optimality of path found. Checks path length doesn't use the extra epsilon transition."""

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

    def test_add_new_state_type_integrity(self) -> None:
        """
        Should properly add new state of different type than original states;
        see <https://github.com/caleb531/automata/issues/60> for more details
        """
        dfa1 = NFA(
            states={"0", "1"},
            input_symbols={"0"},
            transitions={"0": {"0": {"1"}}, "1": {"0": {"1"}}},
            initial_state="0",
            final_states={"1"},
        )

        dfa2 = DFA.from_nfa(dfa1.reverse())

        self.assertEqual(
            dfa1.accepts_input("00"),
            dfa2.accepts_input("00"),
            "DFA and NFA are not equivalent when they should be",
        )

    def test_nfa_equality(self) -> None:
        input_symbols = {"0", "1"}
        nfa1 = NFA(
            states={"s", "a", "b", "c", "d", "e", "f", "g", "h"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"g"}, "1": {"a"}},
                "a": {"0": {"b"}, "": {"d"}},
                "b": {"1": {"c"}},
                "c": {"0": {"a"}},
                "d": {"1": {"e"}, "": {"f"}},
                "e": {"1": {"d"}},
                "f": {"": {"s"}},
                "g": {"1": {"h"}},
                "h": {"0": {"f"}},
            },
            initial_state="s",
            final_states={"s"},
        )

        self.assertEqual(
            nfa1, NFA.from_regex("((1(010)*(11)*)|(010))*", input_symbols=input_symbols)
        )

        nfa2 = NFA(
            states={"s", "a", "b", "c", "d", "e"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"a"}, "1": {"s"}, "": {"b", "d"}},
                "a": {"1": {"s"}},
                "b": {"0": {"b"}, "1": {"c"}},
                "c": {"0": {"c"}, "1": {"e"}},
                "d": {"0": {"c"}, "1": {"d"}},
                "e": {"0": {"c"}},
            },
            initial_state="s",
            final_states={"c"},
        )

        self.assertEqual(
            nfa2,
            NFA.from_regex(
                "(((01) | 1)*)((0*1) | (1*0))(((10) | 0)*)", input_symbols=input_symbols
            ),
        )

        nfa3 = NFA(
            states={"s", "0", "1", "00", "01", "10", "11"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"0"}, "1": {"1"}},
                "0": {"0": {"00"}, "1": {"01"}},
                "1": {"0": {"10"}, "1": {"11"}},
                "00": {"0": {"00"}, "1": {"01"}},
                "01": {"0": {"00"}, "1": {"01"}},
                "10": {"0": {"10"}, "1": {"11"}},
                "11": {"0": {"10"}, "1": {"11"}},
            },
            initial_state="s",
            final_states={"00", "11"},
        )

        self.assertEqual(
            nfa3,
            NFA.from_regex("(0(0 | 1)*0) | (1(0 | 1)*1)", input_symbols=input_symbols),
        )

        nfa4 = NFA(
            states={"s", "0", "1", "00", "01", "10", "11"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"0"}, "1": {"1"}},
                "0": {"0": {"00"}, "1": {"01"}},
                "1": {"0": {"10"}, "1": {"11"}},
                "00": {"0": {"00"}, "1": {"01"}},
                "01": {"0": {"10"}, "1": {"11"}},
                "10": {"0": {"00"}, "1": {"01"}},
                "11": {"0": {"10"}, "1": {"11"}},
            },
            initial_state="s",
            final_states={"00", "11"},
        )

        self.assertEqual(
            nfa4,
            NFA.from_regex("((0 | 1)*00) | ((0 | 1)*11)", input_symbols=input_symbols),
        )

        input_symbols_2 = {"0", "1", "2"}
        nfa5 = NFA(
            states={"s", "a", "b", "c", "d", "e", "f", "g", "h"},
            input_symbols=input_symbols_2,
            transitions={
                "s": {"": {"a", "f", "g"}, "2": {"c"}},
                "a": {"0": {"b", "c"}},
                "b": {"1": {"a"}},
                "c": {"1": {"s", "d"}},
                "d": {"0": {"e"}},
                "e": {"0": {"c"}},
                "f": {"1": {"f"}},
                "g": {"0": {"g"}, "": {"h"}},
                "h": {"2": {"h"}},
            },
            initial_state="s",
            final_states={"f", "h"},
        )

        self.assertEqual(
            nfa5,
            NFA.from_regex(
                "((((01)*0) | 2)(100)*1)*(1* | (0*2*))", input_symbols=input_symbols_2
            ),
        )

    def test_nfa_levenshtein_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (1, 1), (0, 1)},
                    "a": {(0, 1), (1, 1)},
                    "o": {(0, 1), (1, 1)},
                    "d": {(0, 1), (1, 1)},
                    "": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (1, 2), (0, 2)},
                    "a": {(0, 2), (1, 2)},
                    "o": {(0, 2), (1, 2)},
                    "d": {(0, 2), (1, 2)},
                    "": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(1, 1), (2, 0), (2, 1)},
                    "a": {(1, 1), (2, 1)},
                    "f": {(1, 1), (2, 1)},
                    "d": {(1, 1), (2, 1)},
                    "": {(2, 1)},
                },
                (1, 1): {
                    "o": {(1, 2), (2, 1), (2, 2)},
                    "a": {(1, 2), (2, 2)},
                    "f": {(1, 2), (2, 2)},
                    "d": {(1, 2), (2, 2)},
                    "": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(3, 1), (2, 1), (3, 0)},
                    "a": {(3, 1), (2, 1)},
                    "f": {(3, 1), (2, 1)},
                    "d": {(3, 1), (2, 1)},
                    "": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (3, 2), (2, 2)},
                    "a": {(3, 2), (2, 2)},
                    "f": {(3, 2), (2, 2)},
                    "d": {(3, 2), (2, 2)},
                    "": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(3, 1), (4, 0), (4, 1)},
                    "a": {(3, 1), (4, 1)},
                    "f": {(3, 1), (4, 1)},
                    "o": {(3, 1), (4, 1)},
                    "": {(4, 1)},
                },
                (3, 1): {
                    "d": {(3, 2), (4, 1), (4, 2)},
                    "a": {(3, 2), (4, 2)},
                    "f": {(3, 2), (4, 2)},
                    "o": {(3, 2), (4, 2)},
                    "": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {"a": {(4, 1)}, "f": {(4, 1)}, "o": {(4, 1)}, "d": {(4, 1)}},
                (4, 1): {"a": {(4, 2)}, "f": {(4, 2)}, "o": {(4, 2)}, "d": {(4, 2)}},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(nfa, NFA.edit_distance(alphabet, "food", 2))

        nice_nfa = NFA.edit_distance(set(string.ascii_lowercase), "nice", 1)

        self.assertFalse(nice_nfa.accepts_input("food"))

        close_strings = [
            "anice",
            "bice",
            "dice",
            "fice",
            "ice",
            "mice",
            "nace",
            "nice",
            "niche",
            "nick",
            "nide",
            "niece",
            "nife",
            "nile",
            "nine",
            "niue",
            "pice",
            "rice",
            "sice",
            "tice",
            "unice",
            "vice",
            "wice",
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(alphabet, "food", -1)
        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(
                alphabet, "food", 2, insertion=False, deletion=False, substitution=False
            )

    def test_nfa_hamming_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (1, 1)},
                    "d": {(1, 1)},
                    "o": {(1, 1)},
                    "a": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (1, 2)},
                    "d": {(1, 2)},
                    "o": {(1, 2)},
                    "a": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(2, 0), (2, 1)},
                    "d": {(2, 1)},
                    "a": {(2, 1)},
                    "f": {(2, 1)},
                },
                (1, 1): {
                    "o": {(2, 1), (2, 2)},
                    "d": {(2, 2)},
                    "a": {(2, 2)},
                    "f": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(3, 1), (3, 0)},
                    "d": {(3, 1)},
                    "a": {(3, 1)},
                    "f": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (3, 2)},
                    "d": {(3, 2)},
                    "a": {(3, 2)},
                    "f": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(4, 0), (4, 1)},
                    "o": {(4, 1)},
                    "a": {(4, 1)},
                    "f": {(4, 1)},
                },
                (3, 1): {
                    "d": {(4, 1), (4, 2)},
                    "o": {(4, 2)},
                    "a": {(4, 2)},
                    "f": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {},
                (4, 1): {},
                (4, 2): {},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(
            nfa, NFA.edit_distance(alphabet, "food", 2, insertion=False, deletion=False)
        )

        nice_nfa = NFA.edit_distance(
            set(string.ascii_lowercase), "nice", 1, insertion=False, deletion=False
        )

        self.assertFalse(nice_nfa.accepts_input("food"))

        close_strings = [
            "bice",
            "dice",
            "fice",
            "mice",
            "nace",
            "nice",
            "nick",
            "nide",
            "nife",
            "nile",
            "nine",
            "niue",
            "pice",
            "rice",
            "sice",
            "tice",
            "vice",
            "wice",
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        close_strings_insertion_deletion = [
            "anice",
            "nicee",
            "niece",
            "unice",
            "niace",
            "ice",
            "nce",
            "nic",
        ]

        for close_string in close_strings_insertion_deletion:
            self.assertFalse(nice_nfa.accepts_input(close_string))

    def test_nfa_LCS_distance(self) -> None:
        alphabet = {"f", "o", "d", "a"}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {
                    "f": {(1, 0), (0, 1)},
                    "d": {(0, 1)},
                    "a": {(0, 1)},
                    "o": {(0, 1)},
                    "": {(1, 1)},
                },
                (0, 1): {
                    "f": {(1, 1), (0, 2)},
                    "d": {(0, 2)},
                    "a": {(0, 2)},
                    "o": {(0, 2)},
                    "": {(1, 2)},
                },
                (0, 2): {"f": {(1, 2)}},
                (1, 0): {
                    "o": {(1, 1), (2, 0)},
                    "d": {(1, 1)},
                    "a": {(1, 1)},
                    "f": {(1, 1)},
                    "": {(2, 1)},
                },
                (1, 1): {
                    "o": {(1, 2), (2, 1)},
                    "d": {(1, 2)},
                    "a": {(1, 2)},
                    "f": {(1, 2)},
                    "": {(2, 2)},
                },
                (1, 2): {"o": {(2, 2)}},
                (2, 0): {
                    "o": {(2, 1), (3, 0)},
                    "d": {(2, 1)},
                    "a": {(2, 1)},
                    "f": {(2, 1)},
                    "": {(3, 1)},
                },
                (2, 1): {
                    "o": {(3, 1), (2, 2)},
                    "d": {(2, 2)},
                    "a": {(2, 2)},
                    "f": {(2, 2)},
                    "": {(3, 2)},
                },
                (2, 2): {"o": {(3, 2)}},
                (3, 0): {
                    "d": {(3, 1), (4, 0)},
                    "a": {(3, 1)},
                    "f": {(3, 1)},
                    "o": {(3, 1)},
                    "": {(4, 1)},
                },
                (3, 1): {
                    "d": {(3, 2), (4, 1)},
                    "a": {(3, 2)},
                    "f": {(3, 2)},
                    "o": {(3, 2)},
                    "": {(4, 2)},
                },
                (3, 2): {"d": {(4, 2)}},
                (4, 0): {"d": {(4, 1)}, "a": {(4, 1)}, "f": {(4, 1)}, "o": {(4, 1)}},
                (4, 1): {"d": {(4, 2)}, "a": {(4, 2)}, "f": {(4, 2)}, "o": {(4, 2)}},
                (4, 2): {},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3))),
        )

        self.assertEqual(
            nfa, NFA.edit_distance(alphabet, "food", 2, substitution=False)
        )

        close_strings_substitution = ["tice", "nick", "noce"]
        close_strings_insertion = ["anice", "nicee", "niece", "unice", "niace"]
        close_strings_deletion = ["ice", "nce", "nic"]

        nice_nfa_insertion = NFA.edit_distance(
            set(string.ascii_lowercase),
            "nice",
            1,
            insertion=True,
            substitution=False,
            deletion=False,
        )
        nice_nfa_deletion = NFA.edit_distance(
            set(string.ascii_lowercase),
            "nice",
            1,
            deletion=True,
            substitution=False,
            insertion=False,
        )

        for close_string in close_strings_substitution:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_insertion:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertTrue(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_deletion:
            self.assertTrue(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))

    def test_nfa_shuffle_product(self) -> None:
        """
        Test shuffle product of two NFAs.

        Test cases based on https://planetmath.org/shuffleoflanguages
        """
        input_symbols = {"a", "b"}

        # Basic finite language test case
        nfa1 = NFA.from_dfa(DFA.from_finite_language(input_symbols, {"aba"}))
        nfa2 = NFA.from_dfa(DFA.from_finite_language(input_symbols, {"bab"}))

        nfa3 = NFA.from_dfa(
            DFA.from_finite_language(
                input_symbols,
                {
                    "abbaab",
                    "baabab",
                    "ababab",
                    "babaab",
                    "abbaba",
                    "baabba",
                    "ababba",
                    "bababa",
                },
            )
        )

        self.assertEqual(nfa1.shuffle_product(nfa2), nfa3)

        # Regular language test case
        nfa4 = NFA.from_regex("aa", input_symbols=input_symbols)
        nfa5 = NFA.from_regex("b*", input_symbols=input_symbols)

        nfa6 = NFA.from_dfa(
            DFA.of_length(
                input_symbols, min_length=2, max_length=2, symbols_to_count={"a"}
            )
        )

        self.assertEqual(nfa4.shuffle_product(nfa5), nfa6)

        nfa7 = NFA.from_regex("a?a?a?", input_symbols=input_symbols)
        nfa8 = NFA.from_dfa(
            DFA.of_length(input_symbols, max_length=3, symbols_to_count={"a"})
        )

        self.assertEqual(nfa5.shuffle_product(nfa7), nfa8)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa.shuffle_product(self.dfa)  # type: ignore

    def test_nfa_shuffle_product_set_laws(self) -> None:
        """Test set laws for shuffle product"""
        alphabet = {"a", "b"}

        # Language properties test case
        nfa1 = NFA.from_regex("a*b*", input_symbols=alphabet)
        nfa2 = NFA.from_regex("b*a*", input_symbols=alphabet)
        nfa3 = NFA.from_regex("ab*a", input_symbols=alphabet)

        # Commutativity
        self.assertEqual(nfa1.shuffle_product(nfa2), nfa2.shuffle_product(nfa1))
        # Associativity
        self.assertEqual(
            nfa1.shuffle_product(nfa2.shuffle_product(nfa3)),
            nfa1.shuffle_product(nfa2).shuffle_product(nfa3),
        )
        # Distributes over union
        self.assertEqual(
            nfa1.shuffle_product(nfa2.union(nfa3)),
            nfa1.shuffle_product(nfa2).union(nfa1.shuffle_product(nfa3)),
        )

    def test_right_quotient(self) -> None:
        """
        Tests for right quotient operator,
        based on https://www.geeksforgeeks.org/quotient-operation-in-automata/
        """

        # Hardcode simple test case
        alphabet = set(string.ascii_lowercase)

        nfa1 = NFA.from_dfa(
            DFA.from_finite_language(alphabet, {"hooray", "sunray", "defray", "ray"})
        )
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {"ray"}))

        quotient_dfa_1 = DFA.from_nfa(nfa1.right_quotient(nfa2))
        reference_dfa_1 = DFA.from_finite_language(alphabet, {"hoo", "sun", "def", ""})

        self.assertEqual(quotient_dfa_1, reference_dfa_1)

        # More complicated test case
        nfa3 = NFA.from_dfa(
            DFA.from_finite_language({"a", "b"}, {"", "a", "ab", "aba", "abab", "abb"})
        )
        nfa4 = NFA.from_dfa(
            DFA.from_finite_language({"a", "b"}, {"b", "bb", "bbb", "bbbb"})
        )

        quotient_dfa_2 = DFA.from_nfa(nfa3.right_quotient(nfa4))
        reference_dfa_2 = DFA.from_finite_language({"a", "b"}, {"a", "aba", "ab"})

        self.assertEqual(quotient_dfa_2, reference_dfa_2)

        # Test case for regex
        nfa_5 = NFA.from_regex("bba*baa*")
        nfa_6 = NFA.from_regex("ab*")

        quotient_nfa_3 = nfa_5.right_quotient(nfa_6)
        reference_nfa_3 = NFA.from_regex("bba*ba*")

        self.assertEqual(quotient_nfa_3, reference_nfa_3)

        # Other test case for regex
        nfa_7 = NFA.from_regex("a*baa*")
        nfa_8 = NFA.from_regex("ab*")

        quotient_nfa_4 = nfa_7.right_quotient(nfa_8)
        reference_nfa_4 = NFA.from_regex("a*ba*")

        self.assertEqual(quotient_nfa_4, reference_nfa_4)

        # Yet another regex test case
        nfa_9 = NFA.from_regex("a+bc+")
        nfa_10 = NFA.from_regex("c+")

        quotient_nfa_5 = nfa_9.right_quotient(nfa_10)
        reference_nfa_5 = NFA.from_regex("a+bc*")

        self.assertEqual(quotient_nfa_5, reference_nfa_5)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa.right_quotient(self.dfa)  # type: ignore

    def test_left_quotient(self) -> None:
        """
        Tests for left quotient operator,
        based on https://www.geeksforgeeks.org/quotient-operation-in-automata/
        """

        # Hardcode simple test case
        alphabet = set(string.ascii_lowercase)

        nfa1 = NFA.from_dfa(
            DFA.from_finite_language(alphabet, {"match", "matter", "mat", "matzoth"})
        )
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {"mat"}))

        quotient_dfa_1 = DFA.from_nfa(nfa1.left_quotient(nfa2))
        reference_dfa_1 = DFA.from_finite_language(alphabet, {"ch", "ter", "", "zoth"})

        self.assertEqual(quotient_dfa_1, reference_dfa_1)

        # Another simple test case
        nfa3 = NFA.from_dfa(
            DFA.from_finite_language({"0", "1"}, {"10", "100", "1010", "101110"})
        )
        nfa4 = NFA.from_dfa(DFA.from_finite_language({"0", "1"}, {"10"}))

        quotient_dfa_2 = DFA.from_nfa(nfa3.left_quotient(nfa4))
        reference_dfa_2 = DFA.from_finite_language({"0", "1"}, {"", "0", "10", "1110"})

        self.assertEqual(quotient_dfa_2, reference_dfa_2)

        # Test case for regex
        nfa_5 = NFA.from_regex("0*1")
        nfa_6 = NFA.from_regex("01*")

        quotient_nfa_3 = nfa_5.left_quotient(nfa_6)
        reference_nfa_3 = NFA.from_regex("0*1") | NFA.from_regex("")

        self.assertEqual(quotient_nfa_3, reference_nfa_3)

        # Another test case for regex
        nfa_7 = NFA.from_regex("ab*aa*")
        nfa_8 = NFA.from_regex("ab*")

        quotient_nfa_4 = nfa_7.left_quotient(nfa_8)
        reference_nfa_4 = NFA.from_regex("b*aa*")

        self.assertEqual(quotient_nfa_4, reference_nfa_4)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa.left_quotient(self.dfa)  # type: ignore

    def test_quotient_properties(self) -> None:
        """Test some properties of quotients, based on
        https://planetmath.org/quotientoflanguages"""

        nfa1 = NFA.from_regex("(ab*aa*)|(baa+)")
        nfa2 = NFA.from_regex("(aa*b*a)|(b+aaba)")

        nfa1_reversed = nfa1.reverse()
        nfa2_reversed = nfa2.reverse()

        self.assertEqual(
            nfa1.right_quotient(nfa2).reverse(),
            nfa1_reversed.left_quotient(nfa2_reversed),
        )
        self.assertEqual(
            nfa1.left_quotient(nfa2).reverse(),
            nfa1_reversed.right_quotient(nfa2_reversed),
        )

        def is_subset_nfa(nfa_a, nfa_b):
            """Returns true if nfa_a is a subset of nfa_b"""
            return (nfa_a | nfa_b) == nfa_b

        self.assertTrue(
            is_subset_nfa(
                nfa1.left_quotient(nfa2) + nfa2, (nfa1 + nfa2).left_quotient(nfa2)
            )
        )
        self.assertTrue(
            is_subset_nfa(
                nfa2 + nfa1.right_quotient(nfa2), (nfa2 + nfa1).right_quotient(nfa2)
            )
        )
