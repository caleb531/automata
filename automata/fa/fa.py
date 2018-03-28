#!/usr/bin/env python3
"""Classes and methods for working with all finite automata."""

import abc
from automata.shared.automaton import Automaton
import networkx as nx
from nxpd import draw

class FA(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for finite automata."""

    def render(self, show=None):
        G = nx.DiGraph()
        G.graph['dpi'] = 100
        G.graph['rankdir'] = 'RL'
        G.add_nodes_from(self.final_states, style='filled', shape='doublecircle')
        G.add_nodes_from(self.states.difference(self.final_states), shape='circle')
        G.add_nodes_from(["start"], shape='point', color='gray')
        G.add_edges_from([("start", self.initial_state, {'color': 'gray'})])
        edges = []
        for o, trans in self.transitions.items():
            for symbol, d in trans.items():
                edges.append((o, d, {'label': symbol}))
        G.add_edges_from(edges)
        return draw(G, show=show)
