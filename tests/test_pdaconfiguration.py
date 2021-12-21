#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAConfigurations."""

# from unittest.mock import patch

import nose.tools as nose

import tests.test_pda as test_pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack


class TestPDAConfiguration(test_pda.TestPDA):
    """A test class for testing configurations of pushdown automata."""

    def test_config_repr(self) -> None:
        """Should create proper string representation of PDA stack."""
        config = PDAConfiguration('q0', 'ab', PDAStack(['a', 'b']))
        nose.assert_equal(
            repr(config),
            'PDAConfiguration(\'q0\', \'ab\', PDAStack(\'a\', \'b\'))'
        )
