#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc


class TuringMachine(object):
    """An abstract base class for Turing machines."""

    @abc.abstractmethod
    def __init__(self, **kwargs):
        """Initialize a complete Turing machine."""
        pass

    @abc.abstractmethod
    def validate_machine(self):
        """Return True if this machine is internally consistent."""
        pass

    @abc.abstractmethod
    def validate_input(self, input_str):
        """Check if the given string is accepted by this machine."""
        pass


class TuringMachineError(Exception):
    """The base class for all machine-related errors."""

    pass


class HaltError(TuringMachineError):
    """The machine halted at an undefined configuration."""

    pass
