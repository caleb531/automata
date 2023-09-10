# Automata

*Copyright 2016-2023 Caleb Evans*  
*Released under the MIT license*

[![tests](https://github.com/caleb531/automata/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/automata/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=main)](https://coveralls.io/r/caleb531/automata?branch=main)

Automata is a Python 3 library implementing structures and algorithms for manipulating finite automata,
pushdown automata, and Turing machines. The algorithms have been optimized and are capable of
processing large inputs. Visualization logic has also been implemented. This package is suitable for
both researchers wishing to manipulate automata and for instructors teaching courses on theoretical
computer science.

The library requires Python 3.8 or newer.

Huge thanks to [@eliotwrobson][eliotwrobson], [@YtvwlD][YtvwlD],
[@dengl11][dengl11], [@Tagl][Tagl], [@lewiuberg][lewiuberg],
[@CamiloMartinezM][CamiloMartinezM],
[@abhinavsinha‑adrino][abhinavsinha-adrino],
[@EduardoGoulart1][EduardoGoulart1], and
[@khoda81][khoda81] for their invaluable code contributions to
this project! 🎉

[eliotwrobson]: https://github.com/eliotwrobson
[YtvwlD]: https://github.com/YtvwlD
[dengl11]: https://github.com/dengl11
[Tagl]: https://github.com/Tagl
[lewiuberg]: https://github.com/lewiuberg
[CamiloMartinezM]: https://github.com/CamiloMartinezM
[abhinavsinha-adrino]: https://github.com/abhinavsinha-adrino
[EduardoGoulart1]: https://github.com/EduardoGoulart1
[khoda81]: https://github.com/khoda81

## Migrating to v8

If you wish to migrate to Automata v8 from an older version, please follow the
[migration guide][migration].

<!-- the below link must be an absolute URL to be functional in the PyPI README -->
[migration]: https://github.com/caleb531/automata/blob/main/MIGRATION.md

## Installing

You can install the latest version of Automata via pip:

```sh
pip install automata-lib
```

To install the optional visual dependencies, use the `visual` extra:

```sh
pip install 'automata-lib[visual]'
```

## API

Please refer to [the official API Documentation][docs] in the `docs/` directory
of the GitHub repository.

<!-- the below link must be an absolute URL to be functional in the PyPI README -->
[docs]: https://github.com/caleb531/automata/blob/main/docs/README.md

## Contributing

Contributions are always welcome! Take a look at the [contributing guide](.github/CONTRIBUTING.md).
