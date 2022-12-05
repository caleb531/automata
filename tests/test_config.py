#!/usr/bin/env python3
"""Functions for testing the global Automata configuration."""

import unittest
from unittest.mock import patch, MagicMock
from frozendict import frozendict

import automata.base.config as global_config
import automata.base.utils
from automata.fa.dfa import DFA


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.orig_should_validate = global_config.should_validate_automata
        self.orig_ensure_frozen_values = global_config.ensure_frozen_values

    def tearDown(self):
        global_config.should_validate_automata = self.orig_should_validate
        global_config.ensure_frozen_values = self.orig_ensure_frozen_values

    @patch('automata.fa.dfa.DFA.validate')
    def test_disable_validation(self, validate):
        """Should disable automaton validation"""
        global_config.should_validate_automata = False
        DFA.universal_language({0, 1})
        validate.assert_not_called()

    @patch('automata.base.utils.freezeValue')
    def test_disable_ensure_values_are_frozen(self, validate):
        """Should disable the call to freezeValue"""
        global_config.ensure_frozen_values = False
        dfa = DFA(
            states=frozenset(['s1']),
            input_symbols=frozenset('a'),
            transitions=frozendict({'s1': frozendict({'a': 's1'})}),
            initial_state='s1',
            final_states=frozenset(['s1']),
        )
        validate.assert_not_called()

        # Also this should not call ensure freeze nor throw any error
        dfa = DFA(
            states={'s1'},
            input_symbols={'a'},
            transitions={'s1': {'a': 's1'}},
            initial_state='s1',
            final_states={'s1'}
        )
        validate.assert_not_called()

    def test_values_are_frozen(self):
        """Should freeze the values"""
        automata.base.utils.freezeValue = MagicMock(wraps=automata.base.utils.freezeValue)
        global_config.ensure_frozen_values = True
        dfa = DFA(
            states={'s1'},
            input_symbols={'a'},
            transitions={'s1': {'a': 's1'}},
            initial_state='s1',
            final_states={'s1'}
        )
        automata.base.utils.freezeValue.assert_called()
