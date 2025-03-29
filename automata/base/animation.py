from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial
from typing import Optional, TypeVar

import manim
import pygraphviz as pgv

_POINTS_IN_INCH = 72


class Animate:
    """The `Animate` class is the config class to set the behavior of animations."""

    DEFAULT_COLOR = manim.WHITE
    HIGHLIGHT_COLOR = manim.RED
    M = TypeVar("M", bound=manim.Mobject)

    @classmethod
    def default_init(cls, mobject_class: type[M]) -> type[M]:
        return partial(mobject_class, color=cls.DEFAULT_COLOR)

    @classmethod
    def to_default_color(cls, mobject: manim.VMobject) -> manim.ApplyMethod:
        """
        Parameters
        ----------
        mobject : VMobject
            The mobject to change to `DEFAULT_COLOR`, or cancel the highlight.

        Returns
        -------
        ApplyMethod
            The animation for the `Scene` object to `play` to change the mobject to
            `DEFAULT_COLOR`.
        """
        return manim.FadeToColor(mobject, cls.DEFAULT_COLOR)

    @classmethod
    def highlight(cls, mobject: manim.VMobject) -> manim.ApplyMethod:
        """
        Parameters
        ----------
        mobject : VMobject
            The mobject to set the `HIGHLIGHT_COLOR`.

        Returns
        -------
        ApplyMethod
            The animation for the `Scene` object to `play` to highlight the mobject.
        """
        return manim.FadeToColor(mobject, cls.HIGHLIGHT_COLOR)


@dataclass(eq=False)
class _ManimNode(manim.VGroup):
    """
    The `ManimNode` class represents a `Node` object in the `AGraph` object with manim.

    The `ManimNode` class is a `VGroup`. For the convenience, it's also added with:

    Parameters
    ----------
    shape : Dot | Circle | VGroup
        - Dot for the nullnode (the start of the edge pointing the initial node)
        - Circle for non-final state
        - VGroup of a doublecircle for final state
    label: Optional[Text]
        The name of the state (N/A for the nullnode)
    """

    shape: manim.Dot | manim.Circle | manim.VGroup
    label: Optional[manim.Text]

    def __init__(self, node: pgv.Node) -> None:
        """
        Parameters
        ----------
        node : `pygraphviz.Node`
            the node which to based on to construct a FA state.

            `node`'s label is its `attr['label']` if given, otherwise its
            `name` property. Its `attr` contains:
            - 'fontsize': float str,
            - 'height': float str,
            - 'pos': f'{float str},{float str}',
            - 'shape': 'point' or 'circle' or 'doublecircle',
            - 'width': float str (possibly equals to 'height')
        """
        super().__init__(name=node.name)
        radius = float(node.attr["height"]) / 2
        if node.attr["shape"] == "point":
            self.shape = Animate.default_init(manim.Dot)(radius=radius)
            self.add(self.shape)
        elif node.attr["shape"].endswith("circle"):
            circle = Animate.default_init(manim.Circle)(radius=radius)
            self.shape = (
                manim.VGroup(
                    circle,
                    Animate.default_init(manim.Circle)().surround(
                        circle, buffer_factor=0.8
                    ),
                )
                if node.attr["shape"].startswith("double")
                else circle
            )
            self.add(self.shape)
            self.label = Animate.default_init(manim.Text)(
                node.name, font_size=float(node.attr["fontsize"])
            )
            self.add(self.label)
        x, y = (float(pt) / _POINTS_IN_INCH for pt in node.attr["pos"].split(","))
        self.set_x(x)
        self.set_y(y)


@dataclass(eq=False)
class _ManimEdge(manim.VGroup):
    """
    The `ManimEdge` class represents an `Edge` object in the `AGraph` object with manim.

    The `ManimEdge` class is a `VGroup`. For the convenience, it's also added with:

    Parameters
    ----------
    edge : VGroup
        The curved arrow made with a series of `CubricBezier` curves objects and an
        `Arrow` object.
    label : Optional[Text]
        The label on the edge, which is the symbol of the transition.
    """

    edge: manim.VGroup
    label: Optional[manim.Text]

    def __init__(self, edge: pgv.Edge) -> None:
        r"""
        Parameters
        ----------
        edge : `pygraphviz.Edge`
            which to based on to construct a FA transition.<br>
            `edge.attr` may contain:
            - 'arrowsize': float str
            - 'fontsize': float str (not exists when 'label' not exists)
            - 'label': str (may not exists)
            - 'lp': f'{float str},{float str}'
            - 'pos': f'e,{float str},{float str}(\s+{float str},{float str})*'
        """
        super().__init__()
        self.edge = self.__parse_spline(edge.attr["pos"].replace("\\\r", ""))
        self.add(self.edge)
        if label_text := edge.attr["label"]:
            self.label = Animate.default_init(manim.Text)(
                label_text, font_size=float(edge.attr["fontsize"])
            )
            x, y = (float(pt) / _POINTS_IN_INCH for pt in edge.attr["lp"].split(","))
            self.label.set_x(x)
            self.label.set_y(y)
            self.add(self.label)

    @staticmethod
    def __parse_spline(edge_pos: str) -> manim.VGroup:
        """
        Convert the pos attribute of the edge which is a string of spline pattern.

        Parameters
        ----------
        edge_pos : str
            a str of spline pattern:
            - spline = endp point (triple)+
            - point = "%f,%f"
            - endp = "e,"point
            - triple = point point point
        """
        points = edge_pos.split()
        control_points = tuple(
            (*(float(pt) / _POINTS_IN_INCH for pt in point.split(",")), 0)
            for point in points[1:]
        )
        result = manim.VGroup()
        for i in range(0, len(control_points) - 1, 3):
            result.add(
                Animate.default_init(manim.CubicBezier)(*control_points[i : i + 4])
            )
        endp = (*(float(pt) / _POINTS_IN_INCH for pt in points[0].split(",")[1:]), 0)
        result.add(
            Animate.default_init(manim.Arrow)(
                start=control_points[-1],
                end=endp,
                max_tip_length_to_length_ratio=1,
            )
        )
        return result


class _ManimInput(manim.VGroup):
    """The `ManimInput` class represents the input string. The characters of the input
    string are separated with each character is generated to a `Text` object, so that
    you can get each character simply with `[]` operator."""

    def __init__(self, text: str) -> None:
        """
        Generate the input symbols and put them on the top left of the screen.

        Parameters
        ----------
        text : str
            The input string.
        """
        super().__init__(*map(manim.Text, text))
        self.arrange().align_on_border(manim.UL)

    def change_symbol(self, current_index: int) -> Iterable[manim.ApplyMethod]:
        """
        Turn the prior symbol (if there is) to default color and highlight the current
        symbol.

        Parameters
        ----------
        current_index : int
            The index of the current symbol which will be highlighted.

        Returns
        -------
        Iterable[ApplyMethod]
            The animations for the `Scene` object to `play`.
        """
        if current_index >= 0:
            yield Animate.highlight(self[current_index])
            if current_index >= 1:
                yield Animate.to_default_color(self[current_index - 1])

    def clean(self, current_index: int) -> Iterable[manim.ApplyMethod]:
        """
        Cancel all the highlighted elements.

        Parameters
        ----------
        current_index : int
            The highlighted symbol to cancel highlight.

        Returns
        -------
        The animations (maybe none) for `Scene` object to `play`.
        """
        if 0 <= current_index < len(self):
            yield Animate.to_default_color(self[current_index])

    def show_result(self, accept: bool) -> manim.Write:
        """
        Add the result ('→' with an 'accept'/'reject') next to the end of the string.

        Parameters
        ----------
        accept : bool
            The result if the input string is accepted.

        Returns
        -------
        Write
            The animation of writing the result for the `Scene` object to `play`.
        """
        result = Animate.default_init(manim.Text)(
            f"→ {'accept' if accept else 'reject'}"
        )
        if len(self):
            result.next_to(self)
        else:
            result.align_on_border(manim.UL)
        return manim.Write(result)
