"""Functions for displaying and maniuplating Turing machines."""

from typing import Sequence

from automata.tm.configuration import TMConfiguration


def print_configs(validation_generator: Sequence[TMConfiguration]) -> None:
    """
    Print each machine configuration represented by the given sequence.

    Parameters
    ----------
    validation_generator : Sequence[TMConfiguration]
        A sequence containing the TMConfigurations to print.
    """

    for config in validation_generator:
        config.print()
