#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
import pathlib
import typing
import uuid
from collections import defaultdict
from typing import Any, Iterable

import pydot

from automata.base.automaton import Automaton, AutomatonStateT

FAStateT = AutomatonStateT


class IpythonGraph:
    def __init__(self, graph):
        self.graph = graph

    def _repr_mimebundle_(
        self,
        include: typing.Optional[typing.Iterable[str]] = None,
        exclude: typing.Optional[typing.Iterable[str]] = None,
        **_,
    ) -> typing.Dict[str, typing.Union[bytes, str]]:
        mime_method = {
            # 'image/jpeg': self._repr_image_jpeg,
            # 'image/png': self._repr_image_png,
            "image/svg+xml": self._repr_image_svg_xml,
        }

        default_mime_types = {"image/svg+xml"}

        include = set(include) if include is not None else default_mime_types
        include -= set(exclude or [])
        return {mimetype: mime_method[mimetype]() for mimetype in include}

    def _repr_image_jpeg(self):
        """Return the rendered graph as JPEG bytes."""
        return self.graph.create(format="jpeg")

    def _repr_image_png(self):
        """Return the rendered graph as PNG bytes."""
        return self.graph.create(format="png")

    def _repr_image_svg_xml(self):
        """Return the rendered graph as SVG string."""
        return self.graph.create(format="svg", encoding="utf-8")


class IpythonGraph:
    def __init__(self, graph):
        self.graph = graph

    def _repr_mimebundle_(
        self,
        include: typing.Optional[typing.Iterable[str]] = None,
        exclude: typing.Optional[typing.Iterable[str]] = None,
        **_,
    ) -> typing.Dict[str, typing.Union[bytes, str]]:
        mime_method = {
            # 'image/jpeg': self._repr_image_jpeg,
            # 'image/png': self._repr_image_png,
            "image/svg+xml": self._repr_image_svg_xml,
        }

        default_mime_types = {"image/svg+xml"}

        include = set(include) if include is not None else default_mime_types
        include -= set(exclude or [])
        return {mimetype: mime_method[mimetype]() for mimetype in include}

    def _repr_image_jpeg(self):
        """Return the rendered graph as JPEG bytes."""
        return self.graph.create(format="jpeg")

    def _repr_image_png(self):
        """Return the rendered graph as PNG bytes."""
        return self.graph.create(format="png")

    def _repr_image_svg_xml(self):
        """Return the rendered graph as SVG string."""
        return self.graph.create(format="svg").decode()


class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    __slots__ = tuple()

    @staticmethod
    def get_state_name(state_data):
        """
        Get an string representation of a state. This is used for displaying and
        uses `str` for any unsupported python data types.
        """
        if isinstance(state_data, str):
            if state_data == "":
                return "λ"

            return state_data

        if isinstance(state_data, (set, frozenset, list, tuple)):
            inner = ", ".join(FA.get_state_name(sub_data) for sub_data in state_data)
            if isinstance(state_data, (set, frozenset)):
                return "{" + inner + "}"

            if isinstance(state_data, tuple):
                return "(" + inner + ")"

            if isinstance(state_data, list):
                return "[" + inner + "]"

        return str(state_data)

    @abc.abstractmethod
    def iter_states(self):
        """Iterate over all states in the automaton."""

    @abc.abstractmethod
    def iter_transitions(self):
        """
        Iterate over all transitions in the automaton. Each transition is a tuple
        of the form (from_state, to_state, symbol)
        """

    @abc.abstractmethod
    def is_accepted(self, state):
        """Check if a state is an accepting state."""

    @abc.abstractmethod
    def is_initial(self, state):
        """Check if a state is an initial state."""

    def show_diagram(self, path=None, format=None, prog=None, rankdir="LR"):
        """
        Creates the graph associated with this FA.
        """
        graph = pydot.Dot(prog=prog, rankdir=rankdir)

        state_nodes = []
        for state in self.iter_states():
            shape = "doublecircle" if self.is_accepted(state) else "circle"
            node = pydot.Node(self.get_state_name(state), shape=shape)
            # we append the node to a list so that we can add all null nodes to
            # the graph before adding any edges.
            state_nodes.append(node)

            # every edge needs an origin node, so we add a null node for every
            # initial state. This is a hack to make the graph look nicer with
            # arrows that appear to come from nowhere.
            if self.is_initial(state):
                # we use a random uuid to make sure that the null node has a
                # unique id to avoid colliding with other states and null_nodes.
                null_node = pydot.Node(
                    str(uuid.uuid4()),
                    label="",
                    shape="none",
                    width="0",
                    height="0",
                )
                graph.add_node(null_node)
                graph.add_edge(pydot.Edge(null_node, node))

        # add all the nodes to the graph
        # we do this after adding all the null nodes so that the null nodes
        # appear preferably at left of the diagram, or at any direction that is
        # specified by the rankdir
        for node in state_nodes:
            graph.add_node(node)

        # there can be multiple transitions between two states, so we need to
        # group them together and create a single edge with a label that
        # contains all the symbols.
        edge_labels = defaultdict(list)
        for from_state, to_state, symbol in self.iter_transitions():
            label = "ε" if symbol == "" else str(symbol)
            from_node = self.get_state_name(from_state)
            to_node = self.get_state_name(to_state)
            edge_labels[from_node, to_node].append(label)

        for (from_node, to_node), labels in edge_labels.items():
            label = ",".join(labels)
            edge = pydot.Edge(
                from_node,
                to_node,
                label='"' + label + '"',
            )
            graph.add_edge(edge)

        if path is not None:
            path = pathlib.Path(path)
            # if the format is not specified, try to infer it from the file extension
            if format is None:
                # get the file extension without the leading "."
                # e.g. ".png" -> "png"
                file_format = path.suffix.split(".")[-1]
                if file_format in graph.formats:
                    format = file_format

            graph.write(path, format=format)

        return graph

    def _ipython_display_(self):
        """
        Display the graph associated with this FA in Jupyter notebooks
        """
        from IPython.display import display

        graph = self.show_diagram()
        display(IpythonGraph(graph))
