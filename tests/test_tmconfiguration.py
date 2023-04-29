#!/usr/bin/env python3
"""Classes and functions for testing the behavior of PDAConfigurations."""

import tests.test_pda as test_pda
from automata.tm.configuration import TMConfiguration
from automata.tm.tape import TMTape


class TestTMConfiguration(test_pda.TestPDA):
    """A test class for testing configurations of pushdown automata."""

    def test_config_hashability(self):
        self.assertEqual(
            hash(
                TMConfiguration(
                    "q0", TMTape("01", blank_symbol=".", current_position=0)
                )
            ),
            hash(
                TMConfiguration(
                    "q0", TMTape("01", blank_symbol=".", current_position=0)
                )
            ),
        )

    def test_config_repr(self):
        """Should create proper string representation of PDA configuration."""
        config = TMConfiguration(
            "q0", TMTape("01", blank_symbol=".", current_position=0)
        )
        self.assertEqual(repr(config), "TMConfiguration('q0', TMTape('01', '.', 0))")
