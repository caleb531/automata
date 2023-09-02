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
the set of all strings it accepts. Three important families of automata in increasing order of generality are as follows:

1. Finite-state automata
2. Pushdown automata
3. Turing machines

These models are a core component of both computer science education and research, seeing applications in a wide variety of areas. In particular, the ability to manipulate finite-state automata within the context of a software package has seen attention from researchers in the past [@Sutner03]. Similar software has also included
functionality for parsing regular expressions into their corresponding finite-state automata [@brics].

# Statement of need

Although there are other packages in the Python software ecosystem that allow for working with
various kinds of automata, they are often niche and lack things like a comprehensive test suite that
allow for more rapid development. This leads to these packages being unable to adopt features that
would be useful to researchers and students alike, such as sophisticated construction and manipulation
algorithms. Moreover, Python is a popular tool for students and researchers, meaning the availability
of a high-quality software package is likely to encourage the further exploration of these structures
in the academic community.

# The `automata` package

`automata` is a Python package for the manipulation and simulation of automata from the families listed above.
The API is designed to mimic the formal mathematical description of each automaton using built-in Python data structures
(such as sets and dicts).
As a popular high-level language, Python enables greater flexibility and ease of use that is difficult
to achieve with a low-level language (e.g., Rust). Algorithms in the package have been optimized for
performance against benchmarks from tasks arising in research. In addition, Python allows for
greater optimization by the integration of lower-level technologies (e.g., Cython), while still
retaining the same high-level API, allowing for integration of more performant features as-needed by
the user base. The package also has native display integration with Jupyter notebooks, enabling
easy visualization.

Of note are some sophisticated and useful algorithms implemented in the package for finite-state automata:

- An optimized version of the Hopcroft-Karp algorithm to determine whether two deterministic finite automata (DFA) are equivalent [@AlmeidaMR10].

- Thompson's algorithm for converting regular expressions to equivalent nondeterministic finite automata (NFA) [@AhoSU86].

- Hopcroft's algorithm for DFA minimization [@Yingjie09].

- A specialized algorithm for directly constructing a state-minimal DFA accepting a given
finite language [@mihov_schulz_2019].

- A specialized algorithm for directly constructing a minimal DFA recognizing strings containing
a given substring [@Knuth77].

To the authors' knowledge, this is the only Python package implementing all of the algorithms stated above.

`automata` was designed around existing theoretical models of automata, for use by both
mathematically-oriented researchers and in educational contexts. The
included functionality for parsing regular expressions and manipulating finite-state
machines enables fast and accessible exploration of these structures by researchers.
On the educational side, the package includes visualization logic that allows students to
interact with these structures in an exploratory manner, and has already seen usage in
undergraduate courses. `automata` has already been cited in publications [@Erickson23], with more
to come as the package becomes more popular.

`automata` has seen a large number of contributions by external contributors and wide adoption,
demonstrating the demand for a high-quality Python package providing these features. The code is
well-maintained, including a comprehensive test suite and type annotations, meaning new features
can be incorporated from requests by the community at a rapid pace.

# Example usage

![A visualization of `target_words_dfa`. Transitions on characters leading to immediate rejections are omitted.\label{fig:target_words_dfa}](finite_language_dfa.png){ width=100% }

The following example is inspired by the use case described in [@Johnson_2010].
We wish to determine which strings in a given set are within the target edit distance
to a reference string. We will do this with utilities provided by `automata`,
first by initializing a DFA corresponding to a set of target words.

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
A visualization of `target_words_dfa`, generated by the package in a Jupyter notebook,
is depicted in \autoref{fig:target_words_dfa}.

Next, we construct an NFA recognizing all strings within the given edit distance of a
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
the words in the result into a list. The library makes this straightforward and idiomatic.

```python
found_words_dfa = target_words_dfa & words_within_edit_distance_dfa
found_words = list(found_words_dfa)
```

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
