# Automata

*Copyright 2016-2023 Caleb Evans*  
*Released under the MIT license*

[![PyPI version](https://badge.fury.io/py/automata-lib.svg)](https://badge.fury.io/py/automata-lib)
[![tests](https://github.com/caleb531/automata/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/automata/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=main)](https://coveralls.io/r/caleb531/automata?branch=main)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/automata-lib/)
[![status](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af/status.svg)](https://joss.theoj.org/papers/fe4d8521383598038e38bc0c948718af)

- **Documentation**: https://caleb531.github.io/automata/
- **Migration Guide**: https://caleb531.github.io/automata/migration/
- **API**: https://caleb531.github.io/automata/api/

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
[@EduardoGoulart1][EduardoGoulart1],
[@khoda81][khoda81], and
[@christopher-hampson][christopher-hampson] for their invaluable code contributions to
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
[christopher-hampson]: https://github.com/christopher-hampson

## Installing

You can install the latest version of Automata via pip:

```sh
pip install automata-lib
```

To install the optional visual dependencies, use the `visual` extra:

```sh
pip install 'automata-lib[visual]'
```

## Contributing

Contributions are always welcome! Take a look at the [contributing guide](./CONTRIBUTING.md).
