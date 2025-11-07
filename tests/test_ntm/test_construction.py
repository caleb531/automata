"""Tests covering NTM construction and immutability behaviors."""

from unittest.mock import MagicMock, patch

from frozendict import frozendict

from automata.tm.ntm import NTM
from tests.test_ntm.base import NTMTestCase


class TestNTMConstruction(NTMTestCase):
    """Verification for construction-time operations on NTMs."""

    def test_init_ntm(self) -> None:
        """Should copy NTM if passed into NTM constructor."""
        new_ntm = self.ntm1.copy()
        self.assertIsNot(new_ntm, self.ntm1)

    def test_init_ntm_missing_formal_params(self) -> None:
        """Should raise an error if formal NTM parameters are missing."""
        with self.assertRaises(TypeError):
            NTM(  # type: ignore
                states={"q0", "q1", "q2", "q3", "q4"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "x", "y", "."},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q4"},
            )

    @patch("automata.tm.ntm.NTM.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate NTM when initialized."""
        self.ntm1.copy()
        validate.assert_called_once_with()

    def test_copy_ntm(self) -> None:
        """Should create exact copy of NTM if copy() method is called."""
        new_ntm = self.ntm1.copy()
        self.assertIsNot(new_ntm, self.ntm1)

    def test_ntm_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.ntm1.states = set()

    def test_ntm_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.ntm1.states

    def test_ntm_immutable_dict(self) -> None:
        """Should create an NTM whose contents are fully immutable/hashable."""
        self.assertIsInstance(hash(frozendict(self.ntm1.input_parameters)), int)
