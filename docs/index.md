# Automata

*Copyright 2016-2024 Caleb Evans*  
*Released under the MIT license*

[![tests](https://github.com/caleb531/automata/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/automata/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=main)](https://coveralls.io/r/caleb531/automata?branch=main)
[![status](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af/status.svg)](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af)
[![pyOpenSci](https://tinyurl.com/y22nb8up)](https://github.com/pyOpenSci/software-submission/issues/152)


Automata is a Python 3 library implementing structures and algorithms for manipulating finite automata,
pushdown automata, and Turing machines. The algorithms have been optimized and are capable of
processing large inputs. Visualization logic has also been implemented. This package is suitable for
both researchers wishing to manipulate automata and for instructors teaching courses on theoretical
computer science. See [example jupyter notebooks.](https://github.com/caleb531/automata/tree/main/example_notebooks)

For an overview on automata theory, see [this Wikipedia article][wikipedia-article], and
for a more comprehensive introduction to each of these topics, see [these lecture notes][lecture-notes].

[wikipedia-article]: https://en.wikipedia.org/wiki/Automata_theory
[lecture-notes]: https://jeffe.cs.illinois.edu/teaching/algorithms/#models

The library requires Python 3.8 or newer.

## Installing

You can install the latest version of Automata via pip:

```sh
pip install automata-lib
```

To install the optional visual dependencies, use the `visual` extra:

```sh
pip install 'automata-lib[visual]'
```

If you encounter errors building `pygraphviz`, you may need to install `graphviz`.
See the instructions [here](https://graphviz.org/download/).
