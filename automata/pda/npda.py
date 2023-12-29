#!/usr/bin/env python3
"""Classes and methods for working with nondeterministic pushdown automata."""

from typing import AbstractSet, Generator, List, Mapping, Set, Tuple, Union

import automata.base.exceptions as exceptions
import automata.pda.pda as pda
from automata.base.utils import pairwise
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack

NPDAStateT = pda.PDAStateT

NPDAPathT = Mapping[
    str,
    Mapping[str, AbstractSet[Tuple[NPDAStateT, Union[str, Tuple[str, ...]]]]],
]
NPDATransitionsT = Mapping[NPDAStateT, NPDAPathT]

InputPathListT = List[Tuple[PDAConfiguration, PDAConfiguration]]


class NPDA(pda.PDA):
    """
    The `NPDA` class is a subclass of `PDA` and represents a nondeterministic
    pushdown automaton.

    Parameters
    ----------
    states: AbstractSet[NPDAStateT]
        A set of the NPDA's valid states
    input_symbols: AbstractSet[str]
        Set of the NPDA's valid input symbols, each of which is a singleton
        string.
    stack_symbols: AbstractSet[str]
        Set of the NPDA's valid stack symbols, each of which is a singleton
        string.
    transitions: NPDATransitionsT
        A dict consisting of the transitions for each state; see the
        example below for the exact syntax
    initial_state: NPDAStateT
        The name of the initial state for this NPDA.
    initial_stack_symbol: str
        The name of the initial symbol on the stack for this NPDA.
    final_states: AbstractSet[NPDAStateT]
        A set of final states for this NPDA.
    acceptance_mode: pda.PDAAcceptanceModeT, default: "both"
        A string defining whether this NPDA accepts by
        `'final_state'`, `'empty_stack'`, or `'both'`.

    Example
    ----------
        from automata.pda.npda import NPDA
        # NPDA which matches palindromes consisting of 'a's and 'b's
        # (accepting by final state)
        # q0 reads the first half of the word, q1 the other half, q2 accepts.
        # But we have to guess when to switch.
        npda = NPDA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            stack_symbols={'A', 'B', '#'},
            transitions={
                'q0': {
                    '': {
                        '#': {('q2', '#')},  # no change to stack
                    },
                    'a': {
                        '#': {('q0', ('A', '#'))},  # push 'A' to stack
                        'A': {
                            ('q0', ('A', 'A')),  # push 'A' to stack
                            ('q1', ''),  # pop from stack
                        },
                        'B': {('q0', ('A', 'B'))},  # push 'A' to stack
                    },
                    'b': {
                        '#': {('q0', ('B', '#'))},  # push 'B' to stack
                        'A': {('q0', ('B', 'A'))},  # push 'B' to stack
                        'B': {
                            ('q0', ('B', 'B')),  # push 'B' to stack
                            ('q1', ''),  # pop from stack
                        },
                    },
                },
                'q1': {
                    '': {'#': {('q2', '#')}},  # push '#' to (currently empty) stack
                    'a': {'A': {('q1', '')}},  # pop from stack
                    'b': {'B': {('q1', '')}},  # pop from stack
                },
            },
            initial_state='q0',
            initial_stack_symbol='#',
            final_states={'q2'},
            acceptance_mode='final_state'
        )
    """

    __slots__ = (
        "states",
        "input_symbols",
        "stack_symbols",
        "transitions",
        "initial_state",
        "initial_stack_symbol",
        "final_states",
        "acceptance_mode",
    )

    def __init__(
        self,
        *,
        states: AbstractSet[NPDAStateT],
        input_symbols: AbstractSet[str],
        stack_symbols: AbstractSet[str],
        transitions: NPDATransitionsT,
        initial_state: NPDAStateT,
        initial_stack_symbol: str,
        final_states: AbstractSet[NPDAStateT],
        acceptance_mode: pda.PDAAcceptanceModeT = "both",
    ) -> None:
        """Initialize a complete NPDA."""
        super().__init__(
            states=states,
            input_symbols=input_symbols,
            stack_symbols=stack_symbols,
            transitions=transitions,
            initial_state=initial_state,
            initial_stack_symbol=initial_stack_symbol,
            final_states=final_states,
            acceptance_mode=acceptance_mode,
        )

    def iter_transitions(
        self,
    ) -> Generator[Tuple[NPDAStateT, NPDAStateT, Tuple[str, str, str]], None, None]:
        return (
            (from_, to_, (input_symbol, stack_symbol, "".join(stack_push)))
            for from_, input_lookup in self.transitions.items()
            for input_symbol, stack_lookup in input_lookup.items()
            for stack_symbol, op_ in stack_lookup.items()
            for (to_, stack_push) in op_
        )

    def _validate_transition_invalid_symbols(
        self, start_state: NPDAStateT, paths: NPDATransitionsT
    ) -> None:
        """Raise an error if transition symbols are invalid."""
        for input_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(start_state, input_symbol)
            for stack_symbol in symbol_paths:
                self._validate_transition_invalid_stack_symbols(
                    start_state, stack_symbol
                )

    def _get_transitions(
        self, state: NPDAStateT, input_symbol: str, stack_symbol: str
    ) -> Set[Tuple[str, NPDAStateT, str]]:
        """Get the transition tuples for the given state and symbols."""
        transitions = set()
        if (
            state in self.transitions
            and input_symbol in self.transitions[state]
            and stack_symbol in self.transitions[state][input_symbol]
        ):
            for dest_state, new_stack_top in self.transitions[state][input_symbol][
                stack_symbol
            ]:
                transitions.add((input_symbol, dest_state, new_stack_top))
        return transitions

    def _get_next_configurations(
        self, old_config: PDAConfiguration
    ) -> Set[PDAConfiguration]:
        """Advance to the next configurations."""
        transitions: Set[Tuple[str, NPDAStateT, str]] = set()
        if old_config.remaining_input:
            transitions.update(
                self._get_transitions(
                    old_config.state,
                    old_config.remaining_input[0],
                    old_config.stack.top(),
                )
            )
        transitions.update(
            self._get_transitions(old_config.state, "", old_config.stack.top())
        )
        new_configs = set()
        for input_symbol, new_state, new_stack_top in transitions:  # type: ignore
            remaining_input = old_config.remaining_input
            if input_symbol:
                remaining_input = remaining_input[1:]
            new_config = PDAConfiguration(
                new_state,
                remaining_input,
                self._replace_stack_top(old_config.stack, new_stack_top),
            )
            new_configs.add(new_config)
        return new_configs

    def _get_input_path(
        self, input_str: str
    ) -> Tuple[List[Tuple[PDAConfiguration, PDAConfiguration]], bool]:
        """
        Calculate the path taken by input.

        Args:
            input_str (str): The input string to run on the NPDA.

        Returns:
            Tuple[List[Tuple[PDAConfiguration, PDAConfiguration]], bool]: A list
            of all transitions taken in each step and a boolean indicating
            whether the NPDA accepted the input.

        """

        steps = list(self.read_input_stepwise(input_str))

        path: List[PDAConfiguration] = [steps.pop().pop()]

        accepted = path[0] in self.final_states

        for step in reversed(steps):
            if len(step) == 1:
                path.append(step.pop())
                continue

            for curr_step in step:
                if path[-1] in self._get_next_configurations(curr_step):
                    path.append(curr_step)
                    break

        return list(pairwise(reversed(path))), accepted

    def read_input_stepwise(
        self, input_str: str
    ) -> Generator[Set[PDAConfiguration], None, None]:
        """
        Return a generator that yields the configuration of this NPDA at each
        step while reading input.

        Parameters
        ----------
        input_str : str
            The input string to read.

        Yields
        ------
        Generator[Set[PDAConfiguration], None, None]
            A generator that yields the current configuration of
            the NPDA after each step of reading input.

        Raises
        ------
        RejectionException
            Raised if this NPDA does not accept the input string.
        """
        current_configurations = set()
        current_configurations.add(
            PDAConfiguration(
                self.initial_state, input_str, PDAStack([self.initial_stack_symbol])
            )
        )

        yield current_configurations

        while current_configurations:
            new_configurations = set()
            for config in current_configurations:
                if self._has_accepted(config):
                    # One accepting configuration is enough.
                    return
                if config.remaining_input:
                    new_configurations.update(self._get_next_configurations(config))
                elif self._has_lambda_transition(config.state, config.stack.top()):
                    new_configurations.update(self._get_next_configurations(config))
            current_configurations = new_configurations
            yield current_configurations

        raise exceptions.RejectionException(
            "the NPDA did not reach an accepting configuration"
        )
