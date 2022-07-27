#!/usr/bin/env python3
"""Classes and functions for testing the behavior of GNFAs."""
import os
import types
import tempfile
from unittest.mock import patch

import unittest

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA


class TestGNFA(test_fa.TestFA):
    """A test class for testing generalised nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_gnfa(self):
        """Should copy GNFA if passed into NFA constructor."""
        new_gnfa = GNFA.copy(self.gnfa)
        self.assert_is_copy_for_gnfa(new_gnfa, self.gnfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            GNFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_state='q1'
            )

    def test_copy_gnfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_gnfa = self.gnfa.copy()
        self.assert_is_copy_for_gnfa(new_gnfa, self.gnfa)

    def test_init_dfa(self):
        """Should convert DFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_dfa(self.dfa)
        self.assertEqual(gnfa.states, {0, 1, 'q2', 'q0', 'q1'})
        self.assertEqual(gnfa.input_symbols, {'0', '1'})
        self.assertEqual(gnfa.transitions, {
            'q0': {'q0': '0', 'q1': '1', 1: None, 'q2': None},
            'q1': {'q0': '0', 'q2': '1', 1: '', 'q1': None},
            'q2': {'q2': '0', 'q1': '1', 1: None, 'q0': None},
            0: {'q0': '', 1: None, 'q1': None, 'q2': None}
        })
        self.assertEqual(gnfa.initial_state, 0)

    def test_init_nfa(self):
        """Should convert NFA to GNFA if passed into GNFA constructor."""
        gnfa = GNFA.from_nfa(self.nfa)
        self.assertEqual(gnfa.states, {0, 1, 'q0', 'q1', 'q2'})
        self.assertEqual(gnfa.input_symbols, {'b', 'a'})
        self.assertEqual(gnfa.transitions, {
            0: {1: None, 'q0': '', 'q1': None, 'q2': None},
            'q0': {1: None, 'q0': None, 'q1': 'a', 'q2': None},
            'q1': {1: '', 'q0': None, 'q1': 'a', 'q2': ''},
            'q2': {1: None, 'q0': 'b', 'q1': None, 'q2': None}})
        self.assertEqual(gnfa.initial_state, 0)

    @patch('automata.fa.gnfa.GNFA.validate')
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        GNFA.copy(self.gnfa)
        validate.assert_called_once_with()

    def test_gnfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_gnfa = self.gnfa.copy()
        self.assertTrue(self.gnfa == new_gnfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_gnfa = self.gnfa.copy()
        new_gnfa.states.add('q2')
        self.assertTrue(self.nfa != new_gnfa, 'NFAs are equal')

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidRegExError):
            self.gnfa.transitions['q1']['q2'] = {'c'}
            self.gnfa.validate()

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            self.nfa.transitions['q1']['q3'] = {'a'}
            self.nfa.validate()

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.gnfa.initial_state = 'q3'
            self.gnfa.validate()

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            del self.gnfa.transitions[self.gnfa.initial_state]
            self.gnfa.validate()

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            self.gnfa.final_state = 'q3'
            self.gnfa.validate()

    def test_validate_final_state_transition(self):
        """Should raise error if there are transitions from final state"""
        with self.assertRaises(exceptions.InvalidStateError):
            self.gnfa.transitions[self.gnfa.final_state] = self.gnfa.transitions[self.gnfa.initial_state]
            self.gnfa.validate()

    def test_validate_missing_state(self):
        """Should raise an error if some transitions are missing."""
        with self.assertRaises(exceptions.MissingStateError):
            self.gnfa.states.add('q3')
            self.gnfa.validate()

    def test_validate_incomplete_transitions(self):
        """
        Should raise error if transitions from (except final state)
        and to (except initial state) every state is missing.
        """
        gnfa2 = self.gnfa.copy()
        gnfa3 = self.gnfa.copy()
        with self.assertRaises(exceptions.MissingStateError):
            del self.gnfa.transitions['q1']['q0']
            self.gnfa.validate()

        with self.assertRaises(exceptions.MissingStateError):
            del gnfa2.transitions['q_in']['q_f']
            gnfa2.validate()

        with self.assertRaises(exceptions.InvalidStateError):
            gnfa3.transitions['q_in']['q5'] = {}
            gnfa3.validate()

    def test_from_dfa(self):
        """
        Check if GNFA is generated properly from DFA
        """

        dfa = DFA(
            states={0, 1, 2, 4},
            input_symbols={'a', 'b'},
            initial_state=0,
            final_states={4},
            transitions={
                0: {'a': 1, 'b': 2},
                1: {'a': 2, 'b': 2},
                2: {'b': 4}
            },
            allow_partial=True
        )

        gnfa = GNFA.from_dfa(dfa)

        gnfa2 = GNFA(
            states = {0, 1, 2, 3, 4, 5},
            input_symbols={'a', 'b'},
            initial_state=3,
            final_state=5,
            transitions={
                0: {1: 'a', 2: 'b', 0: None, 4: None, 5: None},
                1: {2: 'a|b', 0: None, 1: None, 4: None, 5: None},
                2: {4: 'b', 0: None, 1: None, 2: None, 5: None},
                3: {0: '', 1: None, 2: None, 4: None, 5: None},
                4: {5: '', 0: None, 1: None, 2: None, 4: None}}
        )

        self.assertEqual(gnfa, gnfa2)

    def test_from_nfa(self):
        """Should convert NFA to GNFA properly"""

        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1}, 'b': {1}, '': {1}},
                1: {'a': {1, 2}, '': {2, 4}},
                2: {'': {0}, 'b': {0, 4}}
            },
            initial_state=0,
            final_states={4}
        )

        gnfa = GNFA.from_nfa(nfa)

        gnfa2 = GNFA(
            states = {0, 1, 2, 3, 4, 5},
            initial_state=3,
            final_state=5,
            input_symbols={'a', 'b'},
            transitions={
                0: {1: '(a|b)?', 0: None, 2: None, 4: None, 5: None},
                1: {1: 'a', 2: 'a?', 4: '', 0: None, 5: None},
                2: {0: 'b?', 4: 'b', 1: None, 2: None, 5: None},
                4: {5: '', 0: None, 1: None, 2: None, 4: None},
                3: {0: '', 1: None, 2: None, 4: None, 5: None}
            }
        )

        self.assertEqual(gnfa, gnfa2)

    def test_to_regex(self):
        """
        We generate GNFA from DFA then convert it to regex
        then generate NFA from regex (already tested method)
        and check for equivalence of NFA and previous DFA
        """

        nfa = NFA.from_regex('(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))')
        gnfa = GNFA.from_nfa(nfa)
        regex = gnfa.to_regex()
        nfa = NFA.from_regex(regex)
        dfa2 = DFA.from_nfa(nfa)

        dfa = DFA.from_nfa(nfa)

        self.assertEqual(dfa, dfa2)

    def test_show_diagram_showNone(self):
        """
        Should construct the diagram for a GNFA when show_None = False
        """

        gnfa = self.gnfa

        graph = gnfa.show_diagram(show_None=False)
        self.assertEqual(
            {node.get_name() for node in graph.get_nodes()},
            gnfa.states)
        self.assertEqual(graph.get_node(gnfa.initial_state)[0].get_style(), 'filled')
        self.assertEqual(graph.get_node(gnfa.final_state)[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q2')[0].get_peripheries(), None)
        self.assertEqual(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', 'a', 'q1'),
                ('q1', 'a', 'q1'),
                ('q1', '', 'q2'),
                ('q1', '', 'q_f'),
                ('q2', 'b', 'q0'),
                ('q_in', '', 'q0')
            })

    def test_show_diagram_showNone(self):
        """
        Should construct the diagram for a GNFA when show_None = False
        """

        gnfa = self.gnfa

        graph = gnfa.show_diagram()
        self.assertEqual(
            {node.get_name() for node in graph.get_nodes()},
            gnfa.states)
        self.assertEqual(graph.get_node(gnfa.initial_state)[0].get_style(), 'filled')
        self.assertEqual(graph.get_node(gnfa.final_state)[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q2')[0].get_peripheries(), None)
        self.assertEqual(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q_in', '', 'q0'),
                ('q0', 'ø', 'q2'),
                ('q1', '', 'q2'),
                ('q0', 'ø', 'q_f'),
                ('q1', '', 'q_f'),
                ('q_in', 'ø', 'q2'),
                ('q_in', 'ø', 'q1'),
                ('q1', 'a', 'q1'),
                ('q2', 'b', 'q0'),
                ('q2', 'ø', 'q2'),
                ('q_in', 'ø', 'q_f'),
                ('q2', 'ø', 'q1'),
                ('q0', 'ø', 'q0'),
                ('q2', 'ø', 'q_f'),
                ('q0', 'a', 'q1'),
                ('q1', 'ø', 'q0')
            })

    def test_show_diagram_write_file(self):
        """
        Should construct the diagram for a NFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, 'test_gnfa.png')
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.gnfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

