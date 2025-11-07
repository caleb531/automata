"""Shared fixtures for GNFA-related tests."""

import tempfile

import tests.test_fa as test_fa


class GNFATestCase(test_fa.TestFA):
    """Base test case exposing GNFA fixtures."""

    temp_dir_path = tempfile.gettempdir()
