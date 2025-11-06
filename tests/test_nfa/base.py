"""Shared fixtures for NFA-related tests."""

import tempfile

import tests.test_fa as test_fa


class NfaTestCase(test_fa.TestFA):
    """Base test case providing common NFA fixtures."""

    temp_dir_path = tempfile.gettempdir()


__all__ = ["NfaTestCase"]
