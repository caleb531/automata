#!/usr/bin/env python3
"""Functions for displaying and maniuplating Turing machines."""

from typing import Generator

def print_configs(validation_generator : Generator) -> None:
    """Print each machine configuration represented by the given generator."""
    for config in validation_generator:
        config.print()
