#!/usr/bin/env python3
"""Functions for displaying and maniuplating Turing machines."""


def print_configs(validation_generator):
    """Print each machine configuration represented by the given generator."""
    for config in validation_generator:
        config.print()
