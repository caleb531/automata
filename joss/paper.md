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

<!-- TODO include more language like https://joss.theoj.org/papers/10.21105/joss.03608, and maybe pictures and example usage. -->
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

Of note are some sophisticated algorithms implemented in the package for finite-state automata:

- An optimized version of the Hopcroft-Karp algorithm to determine whether two deterministic finite automata (DFA) are equivalent [@AlmeidaMR10].

- Thompson's algorithm for converting regular expressions to equivalent nondeterministic finite automata (NFA) [@AhoSU86].

- Hopcroft's algorithm for DFA minimization [@Yingjie09].

- A specialized algorithm for directly constructing a state-minimal DFA accepting a given
finite language [@mihov_schulz_2019].

To the authors knowledge, this is the only Python package implementing a number of the algorithms stated above. 

`automata` was designed around existing theoretical models of automata, for use by both
mathematically-oriented researchers and in educational contexts. The
included functionality for parsing regular expressions and manipulating finite-state
machines enables fast and accessible exploration of these structures by researchers.
On the educational side, the package includes visualization logic that allows students to
interact with these structures in an exploratory manner, and has already seen usage in
undergraduate courses. The package has already been cited in publications [@Erickson23], with more
to come as the package matures. 

# Example usage

The following example is inspired by the use case described in [@Johnson_2010].
We wish to determine which strings in a given set are within the target edit distance
to a reference string. We will do this by using utilities provided by `automata`,
starting by first initializing DFAs corresponding to the input set.

```python
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
import string

input_symbols = set(string.ascii_lowercase)

target_words = {'these', 'are', 'target', 'words', 'them', 'those'}

target_words_dfa = DFA.from_finite_language(
  input_symbols,
  target_words,
)
```

Next, construct NFA recognizing all strings within the given edit distance of a given
reference string. This construction can again be done with functions provided by the library.
We need to perform an NFA to DFA conversion for later.

```python
reference_string = 'they'
edit_distance = 2

words_within_edit_distance_dfa = DFA.from_nfa(
  NFA.edit_distance(
    input_symbols,
    reference_string,
    edit_distance,
  )
)
```

Finally, we take the intersection of the two DFAs we have constructed and read all of
the words in the result. The library makes this easy.

```python
found_words_dfa = target_words_dfa & words_within_edit_distance_dfa
found_words = list(found_words_dfa)
```

# Acknowledgements

Thanks to [@YtvwlD][YtvwlD], [@dengl11][dengl11], [@Tagl][Tagl],
[@lewiuberg][lewiuberg], [@CamiloMartinezM][CamiloMartinezM],
and [@abhinavsinha‑adrino][abhinavsinha-adrino]
for their invaluable code contributions to this project.

[YtvwlD]: https://github.com/YtvwlD
[dengl11]: https://github.com/dengl11
[Tagl]: https://github.com/Tagl
[lewiuberg]: https://github.com/lewiuberg
[CamiloMartinezM]: https://github.com/CamiloMartinezM
[abhinavsinha-adrino]: https://github.com/abhinavsinha-adrino
[eliotwrobson]: https://github.com/eliotwrobson

# References