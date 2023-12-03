# Base exception classes

[Table of Contents](README.md)

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See
`automata/base/exceptions.py` for these class definitions.

To reference these exceptions (so as to catch them in a `try..except` block or
whatnot), simply import `automata.base.exceptions` however you'd like:

```python
import automata.base.exceptions as exceptions
```

## class AutomatonException(Exception)

A base class from which all other automata exceptions inherit (including finite
automata and Turing machines).

## class InvalidStateError(AutomatonException)

Raised if a specified state does not exist within the automaton's `states`
set.

## class InvalidSymbolError(AutomatonException)

Raised if a specified symbol does not exist within the automaton's `symbols`
set.

## class MissingStateError(AutomatonException)

Raised if a specified transition definition is missing a defined start state.
This error can also be raised if the initial state does not have any transitions
defined.

## class MissingSymbolError(AutomatonException)

Raised if a given symbol is missing where it would otherwise be required for
this type of automaton (e.g. the automaton is missing a transition for one of
the listed symbols).

## class InitialStateError(AutomatonException)

Raised if the initial state fails to meet some required condition for this type
of automaton (e.g. if the initial state is also a final state, which is
prohibited for Turing machines).

## class FinalStateError(AutomatonException)

Raised if a final state fails to meet some required condition for this type of
automaton (e.g. the final state has transitions to other states, which is
prohibited for Turing machines).

## class RejectionException(AutomatonException)

Raised if the automaton did not accept the input string after validating (e.g.
the automaton stopped on a non-final state after validating input).

## class RegexException(AutomatonException)

A base class for all regular expression related errors.

## class InvalidRegexError(AutomatonException)
Raised if the input regular expression is invalid.

## class SymbolMismatchError(AutomatonException)
Raised if input symbols don't match between two automata but are expected to (e.g.
in the creation of a product automaton).

## class EmptyLanguageException(AutomatonException)

Raised if the attempted operation cannot be performed because the associated
language is empty.

## class InfiniteLanguageException(AutomatonException)

Raised if the attempted operation cannot be performed because the associated
language is infinite.

## class DiagramException(AutomatonException)
Raised if a diagram cannot be produced for an automaton.

------

[Table of Contents](README.md)
