"""Construction and immutability tests for deterministic Turing machines."""

from unittest.mock import MagicMock, patch

from frozendict import frozendict

from automata.tm.dtm import DTM
from tests.test_dtm.base import DTMTestCase


class TestDTMConstruction(DTMTestCase):
    """Validate instantiation helpers and immutability guarantees."""

    def test_init_dtm(self) -> None:
        """Should copy DTM if passed into DTM constructor."""
        new_dtm = self.dtm1.copy()
        self.assertIsNot(new_dtm, self.dtm1)

    def test_init_dtm_missing_formal_params(self) -> None:
        """Should raise an error if formal DTM parameters are missing."""
        with self.assertRaises(TypeError):
            DTM(  # type: ignore
                states={"q0", "q1", "q2", "q3", "q4"},
                input_symbols={"0", "1"},
                tape_symbols={"0", "1", "x", "y", "."},
                initial_state="q0",
                blank_symbol=".",
                final_states={"q4"},
            )

    @patch("automata.tm.dtm.DTM.validate")
    def test_init_validation(self, validate: MagicMock) -> None:
        """Should validate DTM when initialized."""
        self.dtm1.copy()
        validate.assert_called_once_with()

    def test_copy_dtm(self) -> None:
        """Should create exact copy of DTM if copy() method is called."""
        new_dtm = self.dtm1.copy()
        self.assertIsNot(new_dtm, self.dtm1)

    def test_dtm_immutable_attr_set(self) -> None:
        with self.assertRaises(AttributeError):
            self.dtm1.states = set()

    def test_dtm_immutable_attr_del(self) -> None:
        with self.assertRaises(AttributeError):
            del self.dtm1.states

    def test_dtm_immutable_dict(self) -> None:
        """Should ensure DTM contents remain hashable."""
        self.assertIsInstance(hash(frozendict(self.dtm1.input_parameters)), int)
