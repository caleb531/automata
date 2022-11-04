#!/usr/bin/env python3
"""Functions for testing the global Automata configuration."""

import unittest
from unittest.mock import patch

import automata.base.config as global_config
from automata.fa.dfa import DFA


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.orig_should_validate = global_config.should_validate_automata

    def tearDown(self):
        global_config.should_validate_automata = self.orig_should_validate

    @patch('automata.fa.dfa.DFA.validate')
    def test_disable_validation(self, validate):
        """Should disable automaton validation"""
        global_config.should_validate_automata = False
        DFA.universal_language({0, 1})
        validate.assert_not_called()
