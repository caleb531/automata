"""Classes and methods for working with all finite automata."""

from __future__ import annotations

import abc
import os
from collections import defaultdict
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union

from automata.base.automaton import Automaton, AutomatonStateT
from automata.base.utils import (
    LayoutMethod,
    create_graph,
    create_unique_random_id,
    save_graph,
)

# Optional imports for use with visual functionality
try:
    import coloraide
    import pygraphviz as pgv
except ImportError:
    _visual_imports = False
else:
    _visual_imports = True


FAStateT = AutomatonStateT


class FA(Automaton, metaclass=abc.ABCMeta):
    """
    The `FA` class is an abstract base class from which all finite automata inherit.
    Every subclass of FA can be rendered natively inside of a Jupyter notebook
    (automatically calling `show_diagram` without any arguments) if installed with
    the `visual` optional dependency.
    """

    __slots__ = tuple()

    @staticmethod
    def _get_edge_name(symbol: str) -> str:
        return "ε" if symbol == "" else str(symbol)

    @abc.abstractmethod
    def iter_transitions(self) -> Generator[Tuple[FAStateT, FAStateT, str], None, None]:
        """
        Iterate over all transitions in the automaton. Each transition is a tuple
        of the form (from_state, to_state, symbol)
        """

        raise NotImplementedError(
            f"iter_transitions is not implemented for {self.__class__}"
        )

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
        Generates a diagram of the associated automaton.

        Parameters
        ----------
        input_str : Optional[str], default: None
            String consisting of input symbols. If set, will add processing of
            the input string to the diagram.
        path : Union[str, os.PathLike, None], default: None
            Path to output file. If None, the output will not be saved.
        horizontal : bool, default: True
            Direction of node layout in the output graph.
        reverse_orientation : bool, default: False
            Reverse direction of node layout in the output graph.
        fig_size : Union[Tuple[float, float], Tuple[float], None], default: None
            Figure size.
        font_size : float, default: 14.0
            Font size in the output graph.
        arrow_size : float, default: 0.85
            Arrow size in the output graph.
        state_separation : float, default: 0.5
            Distance between nodes in the output graph.

        Returns
        ------
        AGraph
            A diagram of the given automaton.
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

        # create unique id to avoid colliding with other states
        null_node = create_unique_random_id()

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

        is_edge_drawn = defaultdict(lambda: False)
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
            for transition_index, (from_state, to_state, symbol) in enumerate(
                input_path, start=1
            ):
                color = interpolation(transition_index / len(input_path))
                label = self._get_edge_name(symbol)

                is_edge_drawn[from_state, to_state, symbol] = True
                graph.add_edge(
                    self._get_state_name(from_state),
                    self._get_state_name(to_state),
                    label=f"<{label} <b>[<i>#{transition_index}</i>]</b>>",
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
            label = self._get_edge_name(symbol)
            edge_labels[from_node, to_node].append(label)

        for (from_node, to_node), labels in edge_labels.items():
            graph.add_edge(
                from_node,
                to_node,
                label=",".join(sorted(labels)),
                arrowsize=arrow_size_str,
                fontsize=font_size_str,
            )

        # Set layout
        graph.layout(prog=layout_method)

        # Write diagram to file
        if path is not None:
            save_graph(graph, path)

        return graph

    @abc.abstractmethod
    def _get_input_path(
        self, input_str: str
    ) -> Tuple[List[Tuple[FAStateT, FAStateT, str]], bool]:
        """Calculate the path taken by input."""

        raise NotImplementedError(
            f"_get_input_path is not implemented for {self.__class__}"
        )

    def _repr_mimebundle_(
        self, *args: Any, **kwargs: Any
    ) -> Dict[str, Union[bytes, str]]:
        return self.show_diagram()._repr_mimebundle_(*args, **kwargs)

    @staticmethod
    def _add_new_state(state_set: Set[FAStateT], start: int = 0) -> int:
        """Adds new state to the state set and returns it"""
        new_state = start
        while new_state in state_set:
            new_state += 1

        state_set.add(new_state)

        return new_state
