"""Construction and immutability tests for nondeterministic pushdown automata."""

from frozendict import frozendict

import automata.pda.exceptions as pda_exceptions
from automata.pda.npda import NPDA
from tests.test_npda.base import NPDATestCase


class TestNPDAConstruction(NPDATestCase):
    """Validate instantiation paths and acceptance mode handling."""

    def test_init_npda(self) -> None:
        """Should copy NPDA if passed into NPDA constructor."""
        new_npda = self.npda.copy()
        self.assertIsNot(new_npda, self.npda)

    def test_init_npda_missing_formal_params(self) -> None:
        """Should raise an error if formal NPDA parameters are missing."""
        with self.assertRaises(TypeError):
            NPDA(  # type: ignore
                states={"q0", "q1", "q2"},
                input_symbols={"a", "b"},
                initial_state="q0",
                final_states={"q0"},
            )

    def test_init_npda_no_acceptance_mode(self) -> None:
        """Should default acceptance mode to "both" when omitted."""
        new_npda = NPDA(
            states={"q0"},
            input_symbols={"a", "b"},
            stack_symbols={"#"},
            transitions={
                "q0": {
                    "a": {"#": {("q0", "")}},
                }
            },
            initial_state="q0",
            initial_stack_symbol="#",
            final_states={"q0"},
        )
        self.assertEqual(new_npda.acceptance_mode, "both")

    def test_init_npda_invalid_acceptance_mode(self) -> None:
        """Should raise an error if the NPDA has an invalid acceptance mode."""
        with self.assertRaises(pda_exceptions.InvalidAcceptanceModeError):
            NPDA(
                states={"q0"},
                input_symbols={"a", "b"},
                stack_symbols={"#"},
                transitions={"q0": {"a": {"#": {("q0", "")}}}},
                initial_state="q0",
                initial_stack_symbol="#",
                final_states={"q0"},
                acceptance_mode="foo",  # type: ignore
            )

    def test_npda_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.npda.states = set()

    def test_npda_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.npda.states

    def test_npda_immutable_dict(self) -> None:
        """Should ensure NPDA contents remain hashable."""
        self.assertIsInstance(hash(frozendict(self.npda.input_parameters)), int)
