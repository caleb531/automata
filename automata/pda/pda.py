#!/usr/bin/env python3
"""Classes and methods for working with all pushdown automata."""

import abc
import os
from collections import defaultdict
from typing import (
    AbstractSet,
    Any,
    DefaultDict,
    Generator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
from automata.base.automaton import Automaton, AutomatonStateT, AutomatonTransitionsT
from automata.base.utils import (
    LayoutMethod,
    create_graph,
    create_unique_random_id,
    save_graph,
)
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
EdgeDrawnDictT = DefaultDict[Tuple[Any, Any, Tuple[str, str, str]], bool]


class PDA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for pushdown automata."""

    __slots__ = tuple()

    stack_symbols: AbstractSet[str]
    initial_stack_symbol: str
    acceptance_mode: PDAAcceptanceModeT

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
        Iterate over all transitions in the automaton.
        Each transition is a tuple of the form
        (from_state, to_state, (input_symbol, stack_top_symbol, stack_push_symbols))
        """

        raise NotImplementedError(
            f"iter_transitions is not implemented for {self.__class__}"
        )

    def show_diagram(
        self,
        input_str: Optional[str] = None,
        with_machine: bool = True,
        with_stack: bool = True,
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
            - input_str (str, optional): String list of input symbols. Defaults to None.
            - with_machine (bool, optional): Constructs the diagram with states and
              transitions. Ignored if `input_str` is None. Default to True.
            - with_stack (bool, optional): Constructs the diagram with stack and its
              operations. Ignored if `input_str` is None. Default to True.
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
        graph = create_graph(
            horizontal, reverse_orientation, fig_size, state_separation
        )

        font_size_str = str(font_size)
        arrow_size_str = str(arrow_size)

        is_edge_drawn: EdgeDrawnDictT = defaultdict(lambda: False)
        if input_str is not None:
            if not (with_machine or with_stack):
                raise exceptions.DiagramException(
                    "Both with_machine and with_stack cannot be False."
                    " This will produce a empty diagram"
                )

            input_path, is_accepted = self._get_input_path(input_str)

            start_color = coloraide.Color("#ff0")
            end_color = (
                coloraide.Color("#0f0") if is_accepted else coloraide.Color("#f00")
            )

            if with_machine:
                # initialize diagram with all states
                graph = self._add_states_diagram(graph, arrow_size_str, font_size_str)

                # add required transitions to show execution of the
                # PDA for the given input string
                graph = self._create_transitions_for_input_diagram(
                    graph,
                    input_path,
                    is_edge_drawn,
                    start_color,
                    end_color,
                    arrow_size_str,
                    font_size_str,
                )

                # add all the necessary transitions between states
                graph = self._add_transitions_diagram(
                    graph, is_edge_drawn, arrow_size_str, font_size_str
                )

            if with_stack:
                # add the stack transitions
                graph = self._create_stack_diagram(
                    input_path,
                    graph,
                    start_color,
                    end_color,
                    font_size_str,
                    arrow_size_str,
                )
        else:
            # initialize diagram with all states
            graph = self._add_states_diagram(graph, arrow_size_str, font_size_str)

            # add all the necessary transitions between states
            graph = self._add_transitions_diagram(
                graph, is_edge_drawn, arrow_size_str, font_size_str
            )

        # Set layout
        graph.layout(prog=layout_method)

        # Write diagram to file
        if path is not None:
            save_graph(graph, path)

        return graph

    def _create_stack_diagram(
        self,
        input_path: List[Tuple[PDAConfiguration, PDAConfiguration]],
        graph: pgv.AGraph,
        start_color: coloraide.Color,
        end_color: coloraide.Color,
        font_size: str,
        arrow_size: str,
    ) -> pgv.AGraph:
        """
        Constructs stack for all the transitions in the `input_path` and
        adds the constructed stacks into `graph`. Returns the same `graph`
        """
        from_node = input_path[0][0]
        label = " | ".join(reversed(from_node.stack))
        graph.add_node(
            from_node,
            label=f" | {label}",
            shape="record",
            arrowsize=arrow_size,
            fontsize=font_size,
        )

        interpolation = coloraide.Color.interpolate(
            [start_color, end_color], space="srgb"
        )

        for i, (c, n) in enumerate(input_path, start=1):
            from_node = n
            label = " | ".join(reversed(from_node.stack))

            color = interpolation(i / len(input_path))

            graph.add_node(
                from_node,
                label=f" | {label}",
                shape="record",
                arrowsize=arrow_size,
                fontsize=font_size,
            )
            graph.add_edge(
                c,
                n,
                label=f"<<b>[<i>#{i}</i>]</b>>",
                arrowsize=arrow_size,
                fontsize=font_size,
                color=color.to_string(hex=True),
                penwidth="2.5",
            )

        return graph

    def _create_transitions_for_input_diagram(
        self,
        graph: pgv.AGraph,
        input_path: List[Tuple[PDAConfiguration, PDAConfiguration]],
        edge_drawn: EdgeDrawnDictT,
        start_color: coloraide.Color,
        end_color: coloraide.Color,
        arrow_size: str,
        font_size: str,
    ) -> pgv.AGraph:
        """
        Add transitions to show execution of the PDA for the given input string
        """

        interpolation = coloraide.Color.interpolate(
            [start_color, end_color], space="srgb"
        )

        # find all transitions in the finite state machine with traversal.
        for transition_index, (from_state, to_state) in enumerate(input_path, start=1):
            color = interpolation(transition_index / len(input_path))

            symbol = self._get_symbol_configuration(from_state, to_state)
            label = self._get_edge_name(*symbol)

            edge_drawn[from_state.state, to_state.state, symbol] = True
            graph.add_edge(
                self._get_state_name(from_state.state),
                self._get_state_name(to_state.state),
                label=f"<{label} <b>[<i>#{transition_index}</i>]</b>>",
                arrowsize=arrow_size,
                fontsize=font_size,
                color=color.to_string(hex=True),
                penwidth="2.5",
            )

        return graph

    def _add_transitions_diagram(
        self,
        graph: pgv.AGraph,
        is_edge_drawn: EdgeDrawnDictT,
        arrow_size: str,
        font_size: str,
    ) -> pgv.AGraph:
        """
        Add transitions to between states
        """

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
                arrowsize=arrow_size,
                fontsize=font_size,
            )

        return graph

    def _add_states_diagram(
        self,
        graph: pgv.AGraph,
        arrow_size: str,
        font_size: str,
    ) -> pgv.AGraph:
        """
        Add all the states of the PDA
        """

        # create unique id to avoid colliding with other states
        null_node = create_unique_random_id()

        graph.add_node(
            null_node,
            label="",
            tooltip=".",
            shape="point",
            fontsize=font_size,
        )
        initial_node = self._get_state_name(self.initial_state)
        graph.add_edge(
            null_node,
            initial_node,
            tooltip="->" + initial_node,
            arrowsize=arrow_size,
        )

        nonfinal_states = map(self._get_state_name, self.states - self.final_states)
        final_states = map(self._get_state_name, self.final_states)
        graph.add_nodes_from(nonfinal_states, shape="circle", fontsize=font_size)
        graph.add_nodes_from(final_states, shape="doublecircle", fontsize=font_size)

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
