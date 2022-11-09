# Base exception classes

[Table of Contents](index.md)

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See
`automata/base/exceptions.py` for these class definitions.

To reference these exceptions (so as to catch them in a `try..except` block or
whatnot), simply import `automata.base.exceptions` however you'd like:

```python
import automata.base.exceptions as exceptions
```

## class AutomatonException

A base class from which all other automata exceptions inherit (including finite
automata and Turing machines).

## class InvalidStateError

Raised if a specified state does not exist within the automaton's `states`
set.

## class InvalidSymbolError

Raised if a specified symbol does not exist within the automaton's `symbols`
set.

## class MissingStateError

Raised if a specified transition definition is missing a defined start state.
This error can also be raised if the initial state does not have any transitions
defined.

## class MissingSymbolError

Raised if a given symbol is missing where it would otherwise be required for
this type of automaton (e.g. the automaton is missing a transition for one of
the listed symbols).

## class InitialStateError

Raised if the initial state fails to meet some required condition for this type
of automaton (e.g. if the initial state is also a final state, which is
prohibited for Turing machines).

## class FinalStateError

Raised if a final state fails to meet some required condition for this type of
automaton (e.g. the final state has transitions to other states, which is
prohibited for Turing machines).

## class RejectionException

Raised if the automaton did not accept the input string after validating (e.g.
the automaton stopped on a non-final state after validating input).

## class RegexException

A base class for all regular expression related errors.

## class InvalidRegexError
Raised if the input regular expression is invalid.

## class SymbolMismatchError
Raised if input symbols don't match between two automata but are expected to (e.g.
in the creation of a product automaton).

## class InfiniteLanguageException

Raised if the attempted operation cannot be performed because the associated
language is infinite. For example, 

------

[Table of Contents](index.md)
