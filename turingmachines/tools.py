#!/usr/bin/env python3
"""Functions for displaying and maniuplating Turing machines."""


def print_config(current_state, tape, max_position_offset):
    """Print the machine's current configuration in a readable form."""
    print('{current_state}: {tape}\n{current_position}'.format(
        current_state=current_state,
        tape=''.join(tape).rjust(
            len(tape) + max_position_offset - tape.position_offset,
            tape.blank_symbol),
        current_position='^'.rjust(
            tape.current_position + max_position_offset +
            len(current_state) + 3),
    ))


def print_configs(validation_generator):
    """Print each machine configuration represented by the given generator."""
    configs = []
    for current_state, tape in validation_generator:
        configs.append((current_state, tape.copy()))
    # The maximum position offset is also the position offset of the last
    # configuration's tape
    max_position_offset = configs[-1][1].position_offset
    for current_state, tape in configs:
        print_config(current_state, tape, max_position_offset)
