# Turing machine exception classes

[Table of Contents](../index.md)

The `automata.tm` package also includes a module for exceptions specific to
Turing machines. You can reference these exception classes like so:

```python
import automata.tm.exceptions as tm_exceptions
```

## class TMException(AutomatonException)

A base class from which all other Turing machine exceptions inherit.

## class InvalidDirectionError(TMException)

Raised if a direction specified in this machine's transition map is not a valid
direction (valid directions include `'L'`, `'R'`, and `'N'`).

## class InconsistentTapesException(TMException)

Raised if the number of tapes defined for the mntm is not consistent with the transitions.

## class MalformedExtendedTape(TMException)

Raised if the extended tape for simulating a mntm as a ntm is not valid.

------

[Table of Contents](../index.md)
