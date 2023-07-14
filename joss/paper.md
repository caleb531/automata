---
title: 'automata: A Python package for simulating and manipulating automata'
tags:
  - Python
  - automata
authors:
  - name: Caleb Evans
    affiliation: 1
  - name: Eliot W. Robson
    orcid: 0000-0002-1476-6715
    corresponding: true
    affiliation: 2
affiliations:
 - name: Department of Computer Science, University of Illinois, Urbana, IL, USA
   index: 2
date: 13 July 2023
bibliography: paper.bib
---

# Summary

Automata are abstract machines used as models of computation, and are a central object of study in theoretical computer science. Given an input string of characters over a fixed alphabet, these machines either accept or reject the string. A language corresponding to an automaton is
the set of all strings it accepts. Three general families of automata in increasing order of generality are as follows:

1. Finite-state automata
2. Pushdown automata
3. Turing machines

The ability to manipulate and interact with these automaton is 

In particular, finite state automata have widespread applications, as their simplicity allows for efficient computation and manipulation. [CITE KLAUS AUTOMATA PACKAGE]

The forces on stars, galaxies, and dark matter under external gravitational
fields lead to the dynamical evolution of structures in the universe. The orbits
of these bodies are therefore key to understanding the formation, history, and
future state of galaxies. The field of "galactic dynamics," which aims to model
the gravitating components of galaxies to study their structure and evolution,
is now well-established, commonly taught, and frequently used in astronomy.
Aside from toy problems and demonstrations, the majority of problems require
efficient numerical tools, many of which require the same base code (e.g., for
performing numerical orbit integration).

``Gala`` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for ``Gala`` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. ``Gala`` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the ``Astropy`` package [@astropy] (``astropy.units`` and
``astropy.coordinates``).

``Gala`` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in ``Gala`` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike. The source code for ``Gala`` has been
archived to Zenodo with the linked DOI: [@zenodo]

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References