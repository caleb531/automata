"""Classes and methods for working with deterministic pushdown automata."""

from typing import AbstractSet, Generator, List, Mapping, Optional, Set, Tuple, Union

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import automata.pda.pda as pda
from automata.base.utils import pairwise
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack

DPDAStateT = pda.PDAStateT

DPDAPathT = Mapping[str, Mapping[str, Tuple[DPDAStateT, Union[str, Tuple[str, ...]]]]]
DPDATransitionsT = Mapping[DPDAStateT, DPDAPathT]


class DPDA(pda.PDA):
    """
    The `DPDA` class is a subclass of `PDA` and represents a deterministic pushdown
    automaton.

    Parameters
    ----------
    states: AbstractSet[DPDAStateT]
        A set of the DPDA's valid states
    input_symbols: AbstractSet[str]
        Set of the DPDA's valid input symbols, each of which is a singleton
        string.
    stack_symbols: AbstractSet[str]
        Set of the DPDA's valid stack symbols, each of which is a singleton
        string.
    transitions: DPDATransitionsT
        A dict consisting of the transitions for each state; see the
        example below for the exact syntax
    initial_state: DPDAStateT
        The name of the initial state for this DPDA.
    initial_stack_symbol: str
        The name of the initial symbol on the stack for this DPDA.
    final_states: AbstractSet[DPDAStateT]
        A set of final states for this DPDA.
    acceptance_mode: pda.PDAAcceptanceModeT, default: "both"
        A string defining whether this DPDA accepts by
        `'final_state'`, `'empty_stack'`, or `'both'`.

    Example
    ----------
        from automata.pda.dpda import DPDA
        # DPDA which which matches zero or more 'a's, followed by the same
        # number of 'b's (accepting by final state)
        dpda = DPDA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a', 'b'},
            stack_symbols={'0', '1'},
            transitions={
                'q0': {
                    'a': {'0': ('q1', ('1', '0'))}  # push '1' to stack
                },
                'q1': {
                    'a': {'1': ('q1', ('1', '1'))},  # push '1' to stack
                    'b': {'1': ('q2', '')}  # pop from stack
                },
                'q2': {
                    'b': {'1': ('q2', '')},  # pop from stack
                    '': {'0': ('q3', ('0',))}  # no change to stack
                }
            },
            initial_state='q0',
            initial_stack_symbol='0',
            final_states={'q3'},
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
        states: AbstractSet[DPDAStateT],
        input_symbols: AbstractSet[str],
        stack_symbols: AbstractSet[str],
        transitions: DPDATransitionsT,
        initial_state: DPDAStateT,
        initial_stack_symbol: str,
        final_states: AbstractSet[DPDAStateT],
        acceptance_mode: pda.PDAAcceptanceModeT = "both",
    ) -> None:
        """Initialize a complete DPDA."""
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
    ) -> Generator[Tuple[DPDAStateT, DPDAStateT, Tuple[str, str, str]], None, None]:
        return (
            (from_, to_, (input_symbol, stack_symbol, "".join(stack_push)))
            for from_, input_lookup in self.transitions.items()
            for input_symbol, stack_lookup in input_lookup.items()
            for stack_symbol, (to_, stack_push) in stack_lookup.items()
        )

    def _validate_transition_invalid_symbols(
        self, start_state: DPDAStateT, paths: DPDATransitionsT
    ) -> None:
        """Raise an error if transition symbols are invalid."""
        for input_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(start_state, input_symbol)
            for stack_symbol in symbol_paths:
                self._validate_transition_isolated_lambda_transitions(
                    start_state, input_symbol, stack_symbol
                )
                self._validate_transition_invalid_stack_symbols(
                    start_state, stack_symbol
                )

    def _validate_transition_lambda_transition_sibling(
        self, start_state: DPDAStateT, sib_path: DPDAPathT
    ) -> None:
        """Check the given sibling path for adjacent lambda transitions."""
        for other_stack_symbol in sib_path:
            if other_stack_symbol in self.transitions[start_state][""]:
                raise pda_exceptions.NondeterminismError(
                    "A symbol transition is adjacent to a "
                    "lambda transition for this DPDA."
                )

    def _validate_transition_isolated_lambda_transitions(
        self, start_state: DPDAStateT, input_symbol: str, stack_symbol: str
    ) -> None:
        """Raise an error if a lambda transition has no sibling transitions."""
        if input_symbol == "":
            sib_transitions = self.transitions[start_state]
            for sib_input_symbol, sib_path in sib_transitions.items():
                if sib_input_symbol != "":
                    self._validate_transition_lambda_transition_sibling(
                        start_state, sib_path
                    )

    def _get_transition(
        self, state: DPDAStateT, input_symbol: str, stack_symbol: str
    ) -> Optional[DPDAPathT]:
        """Get the transiton tuple for the given state and symbols."""
        if (
            state in self.transitions
            and input_symbol in self.transitions[state]
            and stack_symbol in self.transitions[state][input_symbol]
        ):
            return (input_symbol,) + self.transitions[state][input_symbol][stack_symbol]
        else:
            return None

    def _check_for_input_rejection(
        self, current_configuration: PDAConfiguration
    ) -> None:
        """Raise an error if the given config indicates rejected input."""
        if not self._has_accepted(current_configuration):
            raise exceptions.RejectionException(
                "the DPDA stopped in a non-accepting configuration ({}, {})".format(
                    current_configuration.state, current_configuration.stack
                )
            )

    def _get_next_configuration(self, old_config: PDAConfiguration) -> PDAConfiguration:
        """Advance to the next configuration."""
        transitions: Set[Optional[DPDAPathT]] = set()
        if old_config.remaining_input:
            transitions.add(
                self._get_transition(
                    old_config.state,
                    old_config.remaining_input[0],
                    old_config.stack.top(),
                )
            )
        transitions.add(
            self._get_transition(old_config.state, "", old_config.stack.top())
        )
        if None in transitions:
            transitions.remove(None)
        if len(transitions) == 0:
            raise exceptions.RejectionException(
                "The automaton entered a configuration for which no "
                "transition is defined ({}, {}, {})".format(
                    old_config.state,
                    old_config.remaining_input[0],
                    old_config.stack.top(),
                )
            )
        input_symbol, new_state, new_stack_top = transitions.pop()  # type: ignore
        remaining_input = old_config.remaining_input
        if input_symbol:
            remaining_input = remaining_input[1:]
        new_config = PDAConfiguration(
            new_state,
            remaining_input,
            self._replace_stack_top(old_config.stack, new_stack_top),
        )
        return new_config

    def _get_input_path(
        self, input_str: str
    ) -> Tuple[List[Tuple[PDAConfiguration, PDAConfiguration]], bool]:
        """
        Calculate the path taken by input.

        Args:
            input_str (str): The input string to run on the DPDA.

        Returns:
            Tuple[List[Tuple[PDAConfiguration, PDAConfiguration]], bool]: A list
            of all transitions taken in each step and a boolean indicating
            whether the DPDA accepted the input.

        """

        state_history = list(self.read_input_stepwise(input_str))

        path = list(pairwise(state_history))

        last_state = state_history[-1] if state_history else self.initial_state
        accepted = last_state in self.final_states

        return path, accepted

    def read_input_stepwise(
        self, input_str: str
    ) -> Generator[PDAConfiguration, None, None]:
        """
        Return a generator that yields the configuration of this DPDA at each
        step while reading input.

        Parameters
        ----------
        input_str : str
            The input string to read.

        Yields
        ------
        Generator[PDAConfiguration, None, None]
            A generator that yields the current configuration of
            the DPDA after each step of reading input.

        Raises
        ------
        RejectionException
            Raised if this DPDA does not accept the input string.
        """
        current_configuration = PDAConfiguration(
            self.initial_state, input_str, PDAStack([self.initial_stack_symbol])
        )

        yield current_configuration
        while current_configuration.remaining_input or self._has_lambda_transition(
            current_configuration.state, current_configuration.stack.top()
        ):
            current_configuration = self._get_next_configuration(current_configuration)
            yield current_configuration
            if self._has_accepted(current_configuration):
                return
        self._check_for_input_rejection(current_configuration)
