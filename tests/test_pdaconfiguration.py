#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAConfigurations."""

import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack


class TestPDAConfiguration(test_pda.TestPDA):
    """A test class for testing configurations of pushdown automata."""

    def test_config_hashability(self) -> None:
        self.assertEqual(
            hash(PDAConfiguration("q0", "ab", PDAStack(["a", "b"]))),
            hash(PDAConfiguration("q0", "ab", PDAStack(["a", "b"]))),
        )

    def test_config_repr(self) -> None:
        """Should create proper string representation of PDA configuration."""
        config = PDAConfiguration("q0", "ab", PDAStack(["a", "b"]))
        self.assertEqual(
            repr(config),
            "PDAConfiguration('q0', 'ab', PDAStack(('a', 'b')))",  # noqa
        )
