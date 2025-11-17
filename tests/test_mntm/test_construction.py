"""Construction and immutability tests for multitape NTM."""

from unittest.mock import MagicMock, patch

from frozendict import frozendict

from automata.tm.mntm import MNTM
from tests.test_mntm.base import MNTMTestCase


class TestMNTMConstruction(MNTMTestCase):
    """Validate instantiation paths and immutability guarantees."""

    def test_init_mntm(self) -> None:
        """Should copy MNTM if passed into MNTM constructor."""
        new_mntm = self.mntm1.copy()
        self.assertIsNot(new_mntm, self.mntm1)

    def test_init_mntm_missing_formal_params(self) -> None:
        """Should raise an error if formal MNTM parameters are missing."""
        with self.assertRaises(TypeError):
            MNTM(  # type: ignore
                states={"q0", "q1", "q2", "q3", "q4"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "x", "y", "."},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q4"},
            )

    @patch("automata.tm.mntm.MNTM.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate MNTM when initialized."""
        self.mntm1.copy()
        validate.assert_called_once_with()

    def test_copy_ntm(self) -> None:
        """Should create exact copy of MNTM if copy() method is called."""
        new_mntm = self.mntm1.copy()
        self.assertIsNot(new_mntm, self.mntm1)

    def test_mntm_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.mntm1.states = set()

    def test_mntm_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.mntm1.states

    def test_mntm_immutable_dict(self) -> None:
        """Should create a DPDA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.mntm1.input_parameters)), int)
