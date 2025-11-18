"""Runtime behavior and tape interaction tests for multitape NTM."""

import math
import random
import types
from typing import Set, cast

import automata.base.exceptions as exceptions
import automata.tm.exceptions as tm_exceptions
from tests.test_mntm.base import MNTMTestCase


class TestMNTMRuntime(MNTMTestCase):
    """Exercise execution paths, tape utilities, and acceptance helpers."""

    def test_read_extended_tape(self) -> None:
        self.assertEqual(
            self.mntm1._read_extended_tape("10^10_1^00_00#^_", "^"), ("0", "1", "#")
        )
        self.assertEqual(
            self.mntm1._read_extended_tape("1.10_1.00_0.#_", "."), ("1", "1", "0")
        )
        self.assertEqual(
            self.mntm1._read_extended_tape("10#^_00#^_00^_", "^"), ("#", "#", "0")
        )

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "head symbol was found on leftmost end of the extended tape",
        ):
            self.mntm1._read_extended_tape("^10#_1^010#_00^", "^")

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "no head symbol found on one of the virtual tapes",
        ):
            self.mntm1._read_extended_tape("0^10#_1010#_00^_", "^")

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "there must be 1 virtual head for every tape separator symbol",
        ):
            self.mntm1._read_extended_tape("0^1010^10#^", "^")

        with self.assertRaisesRegex(
            tm_exceptions.MalformedExtendedTapeError,
            "more than one head symbol found on one of the virtual tapes",
        ):
            self.mntm1._read_extended_tape("0^101010^_#^_", "^")

    def test_read_input_as_ntm(self) -> None:
        validation_generator = self.mntm2.read_input_as_ntm("#0000")
        configs = list(validation_generator)
        first_config = set(configs[0]).pop()
        self.assertEqual(first_config.state, "q-1")
        self.assertEqual(str(first_config.tape), "TMTape('#^0000_#^_#^_', '#', 0)")
        last_config = set(configs[-1]).pop()
        self.assertEqual(last_config.state, "qf")
        self.assertEqual(
            str(last_config.tape), "TMTape('#0000#^_#0000#^_#XYYY#^_', '#', 23)"
        )

        with self.assertRaises(exceptions.RejectionException):
            for _ in self.mntm2.read_input_as_ntm("#00"):
                pass

        mntms = [self.mntm1, self.mntm2, self.mntm3]
        inputs = ["0110", "#0000", "0101"]

        for mntm, input_str in zip(mntms, inputs):
            self.assertTrue(mntm.accepts_input(input_str))
            configs = list(mntm.read_input_stepwise(input_str))
            final_mntm_config = cast(Set, configs[-1]).pop()

            final_mntm_tape = ""
            for tape in final_mntm_config.tapes:
                curr_tape = "".join(tape.tape)
                curr_tape_pos = tape.current_position + 1
                final_mntm_tape += (
                    curr_tape[:curr_tape_pos] + "^" + curr_tape[curr_tape_pos:] + "_"
                )

            configs = list(mntm.read_input_as_ntm(input_str))
            final_ntm_config = cast(Set, configs[-1]).pop()
            final_ntm_tape = "".join(final_ntm_config.tape.tape)

            self.assertEqual(final_mntm_tape, final_ntm_tape)

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable TM input is given."""
        final_config = self.mntm1.read_input("0101101011").pop()
        self.assertEqual(final_config.state, "q1")
        self.assertEqual(str(final_config.tapes[0]), "TMTape('0101101011#', '#', 10)")
        self.assertEqual(str(final_config.tapes[1]), "TMTape('111111#', '#', 6)")

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.mntm1.read_input_stepwise("0010101111")
        self.assertIsInstance(validation_generator, types.GeneratorType)
        configs = list(validation_generator)
        first_config = configs[0].pop()
        self.assertEqual(first_config.state, "q0")
        self.assertEqual(str(first_config.tapes[0]), "TMTape('0010101111', '#', 0)")
        self.assertEqual(str(first_config.tapes[1]), "TMTape('#', '#', 0)")
        last_config = configs[-1].pop()
        self.assertEqual(last_config.state, "q1")
        self.assertEqual(str(last_config.tapes[0]), "TMTape('0010101111#', '#', 10)")
        self.assertEqual(str(last_config.tapes[1]), "TMTape('111111#', '#', 6)")

    def test_read_input_rejection(self) -> None:
        """Should raise error if the machine halts."""
        with self.assertRaises(exceptions.RejectionException):
            self.mntm1.read_input("2")

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.mntm2.read_input("1")

    def test_accepts_input_true(self) -> None:
        """Should return True if MNTM input is accepted."""
        test_limit = 20
        for i in range(test_limit):
            input_str_1 = ""
            input_str_2 = "#0"
            input_str_3 = "1"
            for _ in range(i):
                k = random.randint(0, 1)
                input_str_1 += str(k)
                input_str_2 += "0"
                input_str_3 += str(k)

            input_str_3 += input_str_3
            self.assertTrue(self.mntm1.accepts_input(input_str_1))
            self.assertTrue(self.mntm3.accepts_input(input_str_3))
            self.assertFalse(
                self.mntm3.accepts_input(input_str_3 + str(random.randint(0, 1)))
            )

            if self.is_perfect_square(len(input_str_2) - 1):
                self.assertTrue(self.mntm2.accepts_input(input_str_2))
            else:
                self.assertFalse(self.mntm2.accepts_input(input_str_2))

    def test_accepts_input_false(self) -> None:
        """Should return False if MNTM input is rejected."""
        self.assertFalse(self.mntm1.accepts_input("000012"))
        self.assertFalse(self.mntm2.accepts_input("#00000"))

    @staticmethod
    def is_perfect_square(number: int) -> bool:
        return number == int(math.sqrt(number)) ** 2
