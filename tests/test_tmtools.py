"""Classes and functions for testing the Turing machine utility functions."""

import contextlib
import io
import unittest
from unittest.mock import MagicMock, call, patch

import automata.tm.tools as tmtools
from automata.tm.configuration import MTMConfiguration, TMConfiguration
from automata.tm.tape import TMTape


class TestTMTools(unittest.TestCase):
    """A test class for testing Turing machine utility functions."""

    config: TMConfiguration
    config2: MTMConfiguration

    def setUp(self) -> None:
        """Provide a configuration for testing."""
        self.config = TMConfiguration(
            "q2",
            TMTape(
                tape="abcdefghij",
                blank_symbol=".",
                current_position=2,
            ),
        )

        self.config2 = MTMConfiguration(
            "q1",
            (
                TMTape(
                    tape="abcdefghij",
                    blank_symbol=".",
                    current_position=2,
                ),
                TMTape(
                    tape="klmnopq",
                    blank_symbol=".",
                    current_position=5,
                ),
            ),
        )

    def test_repr_config(self) -> None:
        """Should return a string representation ot the given configuration."""
        self.assertEqual(
            repr(self.config), "TMConfiguration('q2', TMTape('abcdefghij', '.', 2))"
        )
        self.assertEqual(
            repr(self.config2),
            "MTMConfiguration('q1', (TMTape('abcdefghij', '.', 2), "
            + "TMTape('klmnopq', '.', 5)))",
        )

    def test_print_config(self) -> None:
        """Should print the given configuration to stdout."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.config.print()
        self.assertEqual(
            out.getvalue().rstrip(),
            "{}: {}\n{}".format("q2", "abcdefghij", "^".rjust(7)),
        )

    @patch("automata.tm.configuration.TMConfiguration.print")
    def test_print_configs(self, print_config: MagicMock) -> None:
        """Should print each machine configuration to stdout."""
        tape1 = TMTape(
            tape="01010101",
            blank_symbol=".",
            current_position=0,
        )
        tape2 = TMTape(
            tape="x1010101",
            blank_symbol=".",
            current_position=-1,
        )
        tape3 = TMTape(
            tape="yx1010101",
            blank_symbol=".",
            current_position=-2,
        )
        configs = [
            TMConfiguration("q0", tape1),
            TMConfiguration("q1", tape2),
            TMConfiguration("q2", tape3),
            MTMConfiguration("q1", (tape1, tape2, tape3)),
        ]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tmtools.print_configs(configs)  # type: ignore
            self.assertEqual(print_config.call_args_list, [call(), call(), call()])

    def test_tape_iteration(self) -> None:
        """Should be able to iterate over a Turing machine tape."""
        tape = TMTape(
            tape="abcdef",
            blank_symbol=".",
            current_position=2,
        )
        self.assertEqual(tuple(tape), ("a", "b", "c", "d", "e", "f"))

    def test_get_symbols_as_str(self) -> None:
        """Should print tape contents as a string without spaces."""
        tape = TMTape(
            tape="abcdef",
            blank_symbol=".",
            current_position=2,
        )
        self.assertEqual(tape.get_symbols_as_str(), "abcdef")
