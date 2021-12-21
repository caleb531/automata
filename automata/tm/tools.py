#!/usr/bin/env python3
"""Functions for displaying and maniuplating Turing machines."""

from typing import Iterable

def print_configs(validation_generator : Iterable) -> None:
    """Print each machine configuration represented by the given generator."""
    for config in validation_generator:
        config.print()
