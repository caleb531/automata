#!/usr/bin/env python3
"""Functions for testing the global Automata configuration."""

import unittest
from unittest.mock import MagicMock, patch

from frozendict import frozendict

import automata.base.config as global_config
from automata.fa.dfa import DFA


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.orig_should_validate = global_config.should_validate_automata
        self.orig_allow_mutable_automata = global_config.allow_mutable_automata

    def tearDown(self) -> None:
        global_config.should_validate_automata = self.orig_should_validate
        global_config.allow_mutable_automata = self.orig_allow_mutable_automata

    @patch("automata.fa.dfa.DFA.validate")
    def test_disable_validation(self, validate: MagicMock) -> None:
        """Should disable automaton validation"""
        global_config.should_validate_automata = False
        DFA.universal_language({"0", "1"})
        validate.assert_not_called()

    @patch("automata.base.utils.freeze_value")
    def test_disable_ensure_values_are_frozen(self, freeze_value: MagicMock) -> None:
        """Should enable automaton mutability"""
        global_config.allow_mutable_automata = True
        DFA(
            states=frozenset(["s1"]),
            input_symbols=frozenset("a"),
            transitions=frozendict({"s1": frozendict({"a": "s1"})}),
            initial_state="s1",
            final_states=frozenset(["s1"]),
        )
        freeze_value.assert_not_called()

        # Also this should not call freeze_value nor throw any error
        DFA(
            states={"s1"},
            input_symbols={"a"},
            transitions={"s1": {"a": "s1"}},
            initial_state="s1",
            final_states={"s1"},
        )
        freeze_value.assert_not_called()
