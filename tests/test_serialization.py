"""Tests for automata pickle serialization"""

import pickle

import tests.test_fa as test_fa


class TestSerialization(test_fa.TestFA):
    """
    This tests verifies that the cycle FA -> .pkl -> FA works.
    The test only applies to DFA and NFAs as other classes do not implement equality
    """

    def test_serialize_dfa(self) -> None:
        """Should convert a DFA to pickle serialization and reads it back"""
        s = pickle.dumps(self.dfa)
        dfa = pickle.loads(s)
        self.assertEqual(self.dfa, dfa)

    def test_serialize_nfa(self) -> None:
        """Should convert a NFA to pickled representation and read it back"""
        s = pickle.dumps(self.nfa)
        nfa = pickle.loads(s)
        self.assertEqual(self.nfa, nfa)
