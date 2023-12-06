# Contributing to Automata

## Code of Conduct

When interacting with other users and maintainers, please be sure to abide by
the [Code of Conduct](./CODE_OF_CONDUCT.md).

## Submitting an issue

### Bug reports

If you are submitting a bug report, please answer the following questions:

1. What version of Automata were you using?
2. What were you doing?
3. What did you expect to happen?
4. What happened instead?

Please provide any code to reproduce the issue, if possible.

## New features

If you are requesting a new feature or change or behavior, please describe what
you are looking for, and what value it will add to your use case.

## Modifying the codebase

Automata is an open-source project under the MIT License, so you are welcome and
encouraged to modify the codebase with new fixes and enhancements. Please
observe the following guidelines when submitting pull requests for new fixes or
features:

1. All new code must comply with PEP 8. If you install Automata with
`virtualenv`, the `flake8` package should already be available to you for this
purpose. The only exception to this is that the maximum line length has been
increased from 79 characters to 120 characters.

2. Whether you are introducing a bug fix or a new feature, you *must* add tests
to verify that your code additions function correctly and break nothing else.

3. Please run `coverage run -m nose2 && coverage report` to ensure that code
coverage remains close to 100%.

4. If you are adding a new feature or changing behavior, I ask that you please
update the README appropriately with the relevant documentation.

### Configuring a virtualenv

The dependencies for the project and best run inside a `virtualenv`. For
instructions on how to configure virtual environments in Python, please see the
[Virtual Environments](https://docs.python-guide.org/dev/virtualenvs/)
section of the Hitchhiker's Guide to Python.

### Installing project dependencies

You can install all project dependencies via `pip` (assuming your project
virtualenv is active):

```sh
pip install -r requirements.txt
```

### Running unit tests

The project's unit tests are written using [unittest][unittest] and run using
the [nose2][nose2] Python package. You can run all unit tests via the `nose2`
command.

```sh
nose2
```

[unittest]: https://docs.python.org/3/library/unittest.html
[nose2]: https://docs.nose2.io/en/latest/

### Code coverage

The project currently boasts high code coverage across all source files. New
contributions are expected to maintain this high standard. You can view the
current coverage report via the `coverage` command:

```sh
coverage run -m nose2
coverage report
```

If the coverage ever decreases, you can generate and open a detailed HTML view
of the coverage report like so:

```sh
coverage html
open htmlcov/index.html
```
