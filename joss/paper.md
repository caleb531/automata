---
title: 'automata: A Python package for simulating and manipulating automata'
tags:
  - Python
  - automata
authors:
  - name: Caleb Evans
    affiliation: 1
    corresponding: true
  - name: Eliot W. Robson
    orcid: 0000-0002-1476-6715
    affiliation: 2
affiliations:
 - name: Department of Computer Science, University of Illinois, Urbana, IL, USA
   index: 2
date: 13 July 2023
bibliography: paper.bib
---

# Summary

Automata are abstract machines used to represent models of computation, and are a central object of study in theoretical computer science. Given an input string of characters over a fixed alphabet, these machines either accept or reject the string. A language corresponding to an automaton is
the set of all strings it accepts. Three families of automata in increasing order of generality are as follows:

1. Finite-state automata
2. Pushdown automata
3. Turing machines

These models are a core component of both computer science education and research, seeing applications in a wide variety of areas. In particular, the ability to manipulate finite-state automata within the context of a software package has seen attention from researchers in the past [@Sutner02a]. Similar software has also included
functionality for parsing regular expressions into their corresponding finite-state automata [@brics].

# Statement of need

`automata` is a Python package for the manipulation and simulation of automata from the families listed above.
The API is designed to mimic the formal mathematical description of each automata using built-in Python data structures. As a popular high-level language, Python enables greater flexibility and easy-of-use that is difficult
to achieve with a low-level language (e.g., Rust). The algorithms in the package have been optimized for
performance against benchmarks from tasks arising in research. In addition, Python allows for
greater optimization by the integration of lower-level technologies (e.g., Cython), while still
retaining the same high-level API, allowing for integration of more performant features as-needed by
the user base.

`automata` was designed around existing theoretical models of automata, for use by both
mathematically-oriented researchers and students learning automata theory.


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
