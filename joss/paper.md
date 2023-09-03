---
title: 'automata: A Python package for simulating and manipulating automata'
tags:
  - Python
  - automata
authors:
  - name: Caleb Evans
    orcid: 0009-0000-8896-6800
    affiliation: 1 # Affiliation is required
  - name: Eliot W. Robson
    corresponding: true
    orcid: 0000-0002-1476-6715
    affiliation: 2
affiliations:
 - name: Independent Developer, USA
   index: 1
 - name: Department of Computer Science, University of Illinois, Urbana, IL, USA
   index: 2
date: 16 July 2023
bibliography: paper.bib
---

# Summary

Automata are abstract machines used to represent models of computation, and are a central object of study in theoretical computer science
[@Hopcroft06]. Given an input string of characters over a fixed alphabet, these machines either accept or reject the string. A language corresponding to an automaton is
the set of all strings it accepts. Three important families of automata in increasing order of generality are the following:

1. Finite-state automata
2. Pushdown automata
3. Turing machines

The `automata` package facilitates working with these families by allowing simulation of reading input and higher-level manipulation
of the corresponding languages using specialized algorithms.

# Statement of need

These models are a core component of both computer science education and research, seeing further theoretical work
and applications in a wide variety of areas such as computational biology [@Marschall11] and networking [@Xu16].
In particular, the ability to manipulate finite-state automata within the context of a software package has seen attention from
researchers in the past [@Sutner03]. Similar software has also included
functionality for parsing regular expressions into their corresponding finite-state automata [@brics].

`automata` serves the demand for such a package in the Python software ecosystem. As a popular high-level language, Python enables
significant flexibility and ease of use that directly benefits many users. The package includes a comprehensive test suite,
support for modern language features (including type annotations), and has a large number of different automata,
meeting the demands of users across a wide variety of use cases. In particular, the target audience
is both researchers that wish to manipulate automata and in educational contexts to reinforce understanding about how these
models of computation function.


# The `automata` package

The API of the package is designed to mimic the formal mathematical description of each automaton using built-in Python data structures
(such as sets and dicts). This is for ease of use by those that are unfamiliar with these structures, while also providing performance
suitable for tasks arising in research. In particular, algorithms in the package have been written for tackling
performance on large inputs, incorporating algorithmic optimizations such as only exploring the reachable set of states
in the construction of a new finite-state automaton. The package also has native display integration with Jupyter
notebooks, enabling easy visualization that allows students to interact with these structures in an exploratory manner.

Of note are some sophisticated and useful algorithms implemented in the package for finite-state automata:

- An optimized version of the Hopcroft-Karp algorithm to determine whether two deterministic finite automata (DFA) are equivalent [@AlmeidaMR10].

- The product construction algorithm for binary set operations (union, intersection, etc.) on the languages corresponding to two input DFAs [@Sipser12].

- Thompson's algorithm for converting regular expressions to equivalent nondeterministic finite automata (NFA) [@AhoSU86].

- Hopcroft's algorithm for DFA minimization [@Hopcroft71, @Knuutila01].

- A specialized algorithm for directly constructing a state-minimal DFA accepting a given finite language [@mihov_schulz_2019].

- A specialized algorithm for directly constructing a minimal DFA recognizing strings containing
a given substring [@Knuth77].

To the authors' knowledge, this is the only Python package implementing all of the automata manipulation algorithms stated above.

`automata` has already been cited in publications [@Erickson23], and has seen use in multiple large undergraduate courses in introductory
theoretical computer science at the University of Illinois Urbana-Champaign (roughly 2000 students since Fall 2021). In this instance, the package is being used
both as part of an autograder utility for finite-state automata created by students, and as an exploratory tool for use by students directly.

# Example usage

![A visualization of `target_words_dfa`. Transitions on characters leading to immediate rejections are omitted.\label{fig:target_words_dfa}](finite_language_dfa.png){ width=100% }

The following example is inspired by the use case described in [@Johnson_2010].
We wish to determine which strings in a given set are within the target edit distance
to a reference string. We will first initialize a DFA corresponding to a fixed set of target words
over the alphabet of all lowercase ascii characters.

```python
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
import string

target_words_dfa = DFA.from_finite_language(
  input_symbols=set(string.ascii_lowercase),
  language={'these', 'are', 'target', 'words', 'them', 'those'},
)
```
A visualization of `target_words_dfa`, generated by the package in a Jupyter notebook,
is depicted in \autoref{fig:target_words_dfa}.

Next, we construct an NFA recognizing all strings within a target edit distance of a fixed
reference string, and then immediately convert this to an equivalent DFA. The package provides
builtin functions to make this construction easy, and we use the same alphabet as the DFA that was just created.

```python
words_within_edit_distance_dfa = DFA.from_nfa(
  NFA.edit_distance(
    input_symbols=set(string.ascii_lowercase),
    reference_str='they',
    max_edit_distance=2,
  )
)
```

Finally, we take the intersection of the two DFAs we have constructed and read all of
the words in the output DFA into a list. The library makes this straightforward and idiomatic.

```python
found_words_dfa = target_words_dfa & words_within_edit_distance_dfa
found_words = list(found_words_dfa)
```

The DFA `found_words_dfa` accepts the words in intersection of the languages of the
DFAs given as input. Note the power of this technique is that the DFA `words_within_edit_distance_dfa`
has an infinite language, meaning we could not do this same computation just using the builtin
sets in Python directly (as they always represent a finite collection), although the
syntax used by `automata` is very similar.

# Acknowledgements

Thanks (in no particular order) to GitHub users
[YtvwlD](https://github.com/YtvwlD),
[dengl11](https://github.com/dengl11),
[Tagl](https://github.com/Tagl),
[lewiuberg](https://github.com/lewiuberg),
[CamiloMartinezM](https://github.com/CamiloMartinezM),
[abhinavsinha‑adrino](https://github.com/abhinavsinha-adrino),
[EduardoGoulart1](https://github.com/EduardoGoulart1), and
[khoda81](https://github.com/khoda81)
for their invaluable code contributions to this project.

# References
