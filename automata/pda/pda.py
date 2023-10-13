#!/usr/bin/env python3
"""Classes and methods for working with all pushdown automata."""

import abc
import os
import pathlib
import random
import uuid
from collections import defaultdict
from typing import AbstractSet, Generator, List, Literal, Optional, Tuple, Union

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
from automata.base.automaton import Automaton, AutomatonStateT, AutomatonTransitionsT
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack

# Optional imports for use with visual functionality
try:
    import coloraide
    import pygraphviz as pgv
except ImportError:
    _visual_imports = False
else:
    _visual_imports = True

PDAStateT = AutomatonStateT
PDATransitionsT = AutomatonTransitionsT
PDAAcceptanceModeT = Literal["final_state", "empty_stack", "both"]

LayoutMethod = Literal["neato", "dot", "twopi", "circo", "fdp", "nop"]


class PDA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for pushdown automata."""

    __slots__ = tuple()

    stack_symbols: AbstractSet[str]
    initial_stack_symbol: str
    acceptance_mode: PDAAcceptanceModeT

    @staticmethod
    def _get_state_name(state_data: PDAStateT) -> str:
        """
        Get an string representation of a state. This is used for displaying and
        uses `str` for any unsupported python data types.
        """
        if isinstance(state_data, str):
            if state_data == "":
                return "λ"

            return state_data

        elif isinstance(state_data, (frozenset, tuple)):
            inner = ", ".join(PDA._get_state_name(sub_data) for sub_data in state_data)
            if isinstance(state_data, frozenset):
                if state_data:
                    return "{" + inner + "}"
                else:
                    return "∅"

            elif isinstance(state_data, tuple):
                return "(" + inner + ")"

        return str(state_data)

    @staticmethod
    def _get_edge_name(
        input_symbol: str = "", stack_top_symbol: str = "", stack_push: str = ""
    ) -> str:
        return (
            ("ε" if input_symbol == "" else str(input_symbol))
            + ", "
            + ("ε" if stack_top_symbol == "" else str(stack_top_symbol))
            + " | "
            + ("ε" if stack_push == "" else str(stack_push))
        )

    @staticmethod
    def _get_symbol_configuration(
        from_state: PDAConfiguration, to_state: PDAConfiguration
    ) -> Tuple[str, str, str]:
        if (
            from_state.remaining_input == to_state.remaining_input
            or len(from_state.remaining_input) == 0
        ):
            input_symbol = ""
        else:
            input_symbol = from_state.remaining_input[0]

        stack_top_symbol = from_state.stack.top()

        if len(from_state.stack) == len(to_state.stack) + 1:
            stack_push_symbols = ""
        else:
            stack_push_symbols = "".join(to_state.stack[len(from_state.stack) - 1 :])

        return (input_symbol, stack_top_symbol, stack_push_symbols[::-1])

    @abc.abstractmethod
    def iter_transitions(
        self,
    ) -> Generator[Tuple[PDAStateT, PDAStateT, Tuple[str, str, str]], None, None]:
        """
        Iterate over all transitions in the automaton. Each transition is a tuple
        of the form (from_state, to_state, (input_symbol, stack_top_symbol, stack_push_symbols))
        """

    def show_diagram(
        self,
        input_str: Optional[str] = None,
        path: Union[str, os.PathLike, None] = None,
        *,
        layout_method: LayoutMethod = "dot",
        horizontal: bool = True,
        reverse_orientation: bool = False,
        fig_size: Union[Tuple[float, float], Tuple[float], None] = None,
        font_size: float = 14.0,
        arrow_size: float = 0.85,
        state_separation: float = 0.5,
    ) -> pgv.AGraph:
        """
        Generates the graph associated with the given PDA.
        Args:
            input_str (str, optional): String list of input symbols. Defaults to None.
            - path (str or os.PathLike, optional): Path to output file. If
              None, the output will not be saved.
            - horizontal (bool, optional): Direction of node layout. Defaults
              to True.
            - reverse_orientation (bool, optional): Reverse direction of node
              layout. Defaults to False.
            - fig_size (tuple, optional): Figure size. Defaults to None.
            - font_size (float, optional): Font size. Defaults to 14.0.
            - arrow_size (float, optional): Arrow head size. Defaults to 0.85.
            - state_separation (float, optional): Node distance. Defaults to 0.5.
        Returns:
            AGraph corresponding to the given automaton.
        """

        if not _visual_imports:
            raise ImportError(
                "Missing visualization packages; "
                "please install coloraide and pygraphviz."
            )

        # Defining the graph.
        graph = pgv.AGraph(strict=False, directed=True)

        if fig_size is not None:
            graph.graph_attr.update(size=", ".join(map(str, fig_size)))

        graph.graph_attr.update(ranksep=str(state_separation))
        font_size_str = str(font_size)
        arrow_size_str = str(arrow_size)

        if horizontal:
            rankdir = "RL" if reverse_orientation else "LR"
        else:
            rankdir = "BT" if reverse_orientation else "TB"

        graph.graph_attr.update(rankdir=rankdir)

        # we use a random uuid to make sure that the null node has a
        # unique id to avoid colliding with other states.
        # To be able to set the random seed, took code from:
        # https://nathanielknight.ca/articles/consistent_random_uuids_in_python.html
        null_node = str(
            uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)
        )
        graph.add_node(
            null_node,
            label="",
            tooltip=".",
            shape="point",
            fontsize=font_size_str,
        )
        initial_node = self._get_state_name(self.initial_state)
        graph.add_edge(
            null_node,
            initial_node,
            tooltip="->" + initial_node,
            arrowsize=arrow_size_str,
        )

        nonfinal_states = map(self._get_state_name, self.states - self.final_states)
        final_states = map(self._get_state_name, self.final_states)
        graph.add_nodes_from(nonfinal_states, shape="circle", fontsize=font_size_str)
        graph.add_nodes_from(final_states, shape="doublecircle", fontsize=font_size_str)

        is_edge_drawn: defaultdict = defaultdict(lambda: False)
        if input_str is not None:
            input_path, is_accepted = self._get_input_path(input_str=input_str)

            start_color = coloraide.Color("#ff0")
            end_color = (
                coloraide.Color("#0f0") if is_accepted else coloraide.Color("#f00")
            )
            interpolation = coloraide.Color.interpolate(
                [start_color, end_color], space="srgb"
            )

            # find all transitions in the finite state machine with traversal.
            for transition_index, (from_state, to_state) in enumerate(
                input_path, start=1
            ):
                color = interpolation(transition_index / len(input_path))

                symbol = self._get_symbol_configuration(from_state, to_state)

                is_edge_drawn[from_state.state, to_state.state, symbol] = True
                graph.add_edge(
                    self._get_state_name(from_state.state),
                    self._get_state_name(to_state.state),
                    label=f"<{self._get_edge_name(*symbol)} <b>[<i>#{transition_index}</i>]</b>>",
                    arrowsize=arrow_size_str,
                    fontsize=font_size_str,
                    color=color.to_string(hex=True),
                    penwidth="2.5",
                )

        edge_labels = defaultdict(list)
        for from_state, to_state, symbol in self.iter_transitions():
            if is_edge_drawn[from_state, to_state, symbol]:
                continue

            from_node = self._get_state_name(from_state)
            to_node = self._get_state_name(to_state)
            label = self._get_edge_name(*symbol)
            edge_labels[from_node, to_node].append(label)

        for (from_node, to_node), labels in edge_labels.items():
            graph.add_edge(
                from_node,
                to_node,
                label="\n".join(sorted(labels)),
                arrowsize=arrow_size_str,
                fontsize=font_size_str,
            )

        # Set layout
        graph.layout(prog=layout_method)

        # Write diagram to file. PNG, SVG, etc.
        if path is not None:
            save_path_final: pathlib.Path = pathlib.Path(path)

            format = (
                save_path_final.suffix.split(".")[1] if save_path_final.suffix else None
            )

            graph.draw(
                path=save_path_final,
                format=format,
            )

        return graph

    def _validate_transition_invalid_input_symbols(
        self, start_state: PDAStateT, input_symbol: str
    ) -> None:
        """Raise an error if transition input symbols are invalid."""
        if input_symbol not in self.input_symbols and input_symbol != "":
            raise exceptions.InvalidSymbolError(
                "state {} has invalid transition input symbol {}".format(
                    start_state, input_symbol
                )
            )

    def _validate_transition_invalid_stack_symbols(
        self, start_state: PDAStateT, stack_symbol: str
    ) -> None:
        """Raise an error if transition stack symbols are invalid."""
        if stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                "state {} has invalid transition stack symbol {}".format(
                    start_state, stack_symbol
                )
            )

    def _validate_initial_stack_symbol(self) -> None:
        """Raise an error if initial stack symbol is invalid."""
        if self.initial_stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                "initial stack symbol {} is invalid".format(self.initial_stack_symbol)
            )

    def _validate_acceptance(self) -> None:
        """Raise an error if the acceptance mode is invalid."""
        if self.acceptance_mode not in ("final_state", "empty_stack", "both"):
            raise pda_exceptions.InvalidAcceptanceModeError(
                "acceptance mode {} is invalid".format(self.acceptance_mode)
            )

    @abc.abstractmethod
    def _validate_transition_invalid_symbols(
        self, start_state: PDAStateT, paths: PDATransitionsT
    ) -> None:
        pass

    @abc.abstractmethod
    def _get_input_path(
        self, input_str: str
    ) -> Tuple[List[Tuple[PDAConfiguration, PDAConfiguration]], bool]:
        """Calculate the path taken by input."""

        raise NotImplementedError(
            f"_get_input_path is not implemented for {self.__class__}"
        )

    def validate(self) -> None:
        """Return True if this PDA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_stack_symbol()
        self._validate_final_states()
        self._validate_acceptance()

    def _has_lambda_transition(self, state: PDAStateT, stack_symbol: str) -> bool:
        """Return True if the current config has any lambda transitions."""
        return (
            state in self.transitions
            and "" in self.transitions[state]
            and stack_symbol in self.transitions[state][""]
        )

    def _replace_stack_top(self, stack: PDAStack, new_stack_top: str) -> PDAStack:
        """Replace the top of the PDA stack with another symbol"""
        if new_stack_top == "":
            new_stack = stack.pop()
        else:
            new_stack = stack.replace(new_stack_top)
        return new_stack

    def _has_accepted(self, current_configuration: PDAConfiguration) -> bool:
        """Check whether the given config indicates accepted input."""
        # If there's input left, we're not finished.
        if current_configuration.remaining_input:
            return False
        if self.acceptance_mode in ("empty_stack", "both"):
            # If the stack is empty, we accept.
            if not current_configuration.stack:
                return True
        if self.acceptance_mode in ("final_state", "both"):
            # If current state is a final state, we accept.
            if current_configuration.state in self.final_states:
                return True
        # Otherwise, not.
        return False
