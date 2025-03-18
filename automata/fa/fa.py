"""Classes and methods for working with all finite automata."""

from __future__ import annotations

import abc
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterable, List, Optional, Set, Tuple, Union

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
    import manim
    import pygraphviz as pgv

    from automata.base.animation import Animate, ManimEdge, ManimInput, ManimNode
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


if _visual_imports:

    class FAGraph(manim.VDict):
        """
        The `FAGraph` class is the common class for FA to draw a picture of a `FA`
        object by representing the `AGraph` object generated by `fa.show_diagram()` with
        manim.

        The `FAGraph` class is a `VDict`. The keys are the states (with type `FAStateT`)
        and the transitions (with type `tuple[FAStateT, FAStateT]`, which is their start
        and end points). Specially, there is another `None` key corresponding to the
        `nullnode` in the `FA.show_diagram`, which is the start point of the arrow
        pointing to the initial state. The values are the Manim objects.
        """

        def __init__(self, fa: FA):
            """
            Parameters
            ----------
            fa : FA
                The FA object to create.

                Note that states are discriminated by `FA._get_state_name`, so states
                are not allowed to have same names. Plus, states are not allowed to be
                named 'None'.
            """
            name_state = {FA._get_state_name(state): state for state in fa.states}
            fa_diagram = fa.show_diagram()
            super().__init__(
                {
                    name_state.get(node): ManimNode(node)
                    for node in fa_diagram.nodes_iter()
                }
                | {
                    tuple(map(name_state.get, edge)): ManimEdge(edge)
                    for edge in fa_diagram.edges_iter()
                }
            )

        def highlight_states(
            self, states: Iterable[FAStateT]
        ) -> Iterable[manim.ApplyMethod]:
            """
            Parameters
            ----------
            states : Iterable[FAStateT]
                the states to highlight.
            Returns
            -------
            `Iterable[ApplyMethod]`
                The animations for the `Scene` object to `play`.
            """
            yield from (
                Animate.highlight(self[new_state])
                for new_state in states
                if new_state is not None
            )

        def change_states(
            self, old_states: Iterable[FAStateT], new_states: Iterable[FAStateT]
        ) -> Iterable[manim.ApplyMethod]:
            """
            Turn `old_states` to default color and highlight the `new_states`.

            States occured in both `old_states` and `new_states` will still be
            highlighted.

            Parameters
            ----------
            old_states : Iterable[FAStateT]
                The states to turn to default color.
            new_states : Iterable[FAStateT]
                The states to highlight.

            Returns
            -------
            Iterable[ApplyMethod]
                The animations for the `Scene` object to `play`.
            """
            yield from (
                Animate.to_default_color(self[old_state]) for old_state in old_states
            )
            yield from self.highlight_states(new_states)

        def change_transitions(
            self,
            old_transitions: Iterable[tuple[FAStateT, FAStateT]],
            new_transitions: Iterable[tuple[FAStateT, FAStateT]],
        ) -> Iterable[manim.ApplyMethod]:
            """
            Turn `old_transitions` to default color and highlight the `new_transitions`.

            Transitions occured in both `old_transitions` and `new_transitions` will
            still be highlighted.

            Parameters
            ----------
            old_transitions : Iterable[FAStateT]
                The transitions to turn to default color.
            new_transitions : Iterable[FAStateT]
                The transitions to highlight.

            Returns
            -------
            Iterable[ApplyMethod]
                The animations for the `Scene` object to `play`.
            """
            yield from (
                Animate.to_default_color(self[old_transition])
                for old_transition in old_transitions
            )
            yield from (
                Animate.highlight(self[new_transition])
                for new_transition in new_transitions
                if new_transition[-1] is not None
            )

    @dataclass(init=False)
    class FAAnimation(manim.Scene):
        """
        The `FAAnimation` class is the common base of `DFAAnimation` and `NFAAnimation`.

        Parameters
        ----------
        fa_graph : FAGraph
            The diagram of the `FA` object, will be shown on the down side of the
            animation.
        fa_input : FAInput
            The input string, will be shown on the top left of the animation.
        """

        fa_graph: FAGraph
        fa_input: ManimInput

        def setup(self) -> None:
            """Put the diagram on the down side and the input string on the top left."""
            self.add(
                self.fa_graph.scale_to_fit_width(manim.config.frame_width)
                .align_on_border(manim.LEFT, buff=0)
                .align_on_border(manim.DOWN)
            )
            self.add(self.fa_input.align_on_border(manim.UL))
            self.fa_graph[None].set_color(Animate.HIGHLIGHT_COLOR)

        def clean(
            self, transitions: Iterable[tuple[FAStateT, FAStateT]], current_index: int
        ) -> Iterable[manim.ApplyMethod]:
            """
            Cancel all the highlighted elements.

            Parameters
            ----------
            transitions : Iterable[tuple[FAStateT, FAStateT]]
                The highlighed transitions to cancel the highlight.
            current_index : int
                The highlighted symbol to cancel highlight.

            Returns
            -------
            The animations for `Scene` object to `play`.
            """
            yield Animate.to_default_color(self.fa_input[current_index])
            yield from (
                Animate.to_default_color(self.fa_graph[transition])
                for transition in transitions
                if transition[1] is not None
            )
