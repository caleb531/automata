#!/usr/bin/env python3
"""Tests for automata pickle serialization"""

import pickle

import tests.test_fa as test_fa


class TestSerialization(test_fa.TestFA):
    """
    This tests verifies that the cycle FA -> .pkl -> FA works.
    The test only applies to DFA and NFAs as other classes do not implement equality
    """

    def test_serialize_dfa(self):
        s = pickle.dumps(self.dfa)
        dfa = pickle.loads(s)
        self.assertEqual(self.dfa, dfa)

    def test_serialize_nfa(self):
        s = pickle.dumps(self.nfa)
        nfa = pickle.loads(s)
        self.assertEqual(self.nfa, nfa)
