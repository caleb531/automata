---
author: "Lewi Lie Uberg"
---

# Automata <!-- omit in toc -->

_Copyright 2016-2022 Caleb Evans_
_Released under the MIT license_

[![tests](https://github.com/caleb531/automata/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/automata/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=main)](https://coveralls.io/r/caleb531/automata?branch=main)
[![status](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af/status.svg)](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af)


Automata is a Python 3 library implementing structures and algorithms for manipulating finite automata,
pushdown automata, and Turing machines. The algorithms have been optimized and are capable of
processing large inputs. Visualization logic has also been implemented. This package is suitable for
both researchers wishing to manipulate automata and for instructors teaching courses on theoretical
computer science.

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
