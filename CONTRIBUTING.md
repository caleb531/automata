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

1. All new code must comply with the enabled ruff lint rules.
If you install Automata dependencies with [`uv`](https://github.com/astral-sh/uv), the `ruff`
package should be available to you for this purpose with the config in `pyproject.toml`.
The included VSCode configuration is set to run this formatting on save.

In addition, new code must include type annotations and pass typechecking run with
[mypy](https://mypy.readthedocs.io/en/stable/).

2. Whether you are introducing a bug fix or a new feature, you *must* add tests
to verify that your code additions function correctly and break nothing else.

3. Please run `uv run -- coverage run -m nose2 && uv run -- coverage report` and ensure that your
changes are covered.

4. If you are adding a new feature or changing behavior, please
update the documentation appropriately with the relevant information. This
includes updating docstrings for all functions in the public interface, using
the [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html). To
run the documentation site locally, install the documentation dependencies
with:

```sh
uv sync --group docs
```

Then, start the local server with the following command:

```sh
uv run -- mkdocs serve
```


### Setting up your environment

The dependencies for the project are best managed with [`uv`][uv]. For
instructions on how to install `uv`, see the [uv documentation][installation].

[uv]: https://github.com/astral-sh/uv
[installation]: https://github.com/astral-sh/uv#installation

To create a virtual environment and install all project dependencies (including
dev dependencies), run:

```sh
uv sync
```

To install all dependencies related to the documentation site, run:

```sh
uv sync --group docs
```

#### Troubleshooting pygraphviz

If you run into any trouble building the wheel for `pygraphviz` on macOS when
installing dependencies, try running:

```sh
brew install graphviz
python3 -m pip install -U --no-cache-dir  \
        --config-settings="--global-option=build_ext" \
        --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
        --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
        pygraphviz==1.10
# Proceed to install dependencies
uv sync
```

### Running unit tests

The project's unit tests are written using [unittest][unittest] and run using
the [nose2][nose2] Python package. You can run all unit tests via the following command:

```sh
uv run -- nose2
```

[unittest]: https://docs.python.org/3/library/unittest.html
[nose2]: https://docs.nose2.io/en/latest/

### Code coverage

The project currently boasts high code coverage across all source files. New
contributions are expected to maintain this high standard. You can view the
current coverage report via the following commands:

```sh
uv run -- coverage run -m nose2
uv run -- coverage report
```

If the coverage ever decreases, you can generate and open a detailed HTML view
of the coverage report like so:

```sh
uv run -- coverage html
open htmlcov/index.html
```
