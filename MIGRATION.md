# Automata Migration Guide

*Copyright 2016-2019 Caleb Evans*  
*Released under the MIT license*

## Backwards-incompatible changes from v2 to v3

There have been a number of backwards-incompatible changes from Automata v2 to
v3 to support the new features, including:

## Some types made immutable

The `PDAStack` type is now immutable and hashable; it still represents the
current stack of a PDA.

Likewise, the `TMTape` is now immutable and hashable; it still represents the
tape of a TM and the current cursor position.

## copy() methods removed for (now) immutable types

The `copy` methods on `TMTape` and `PDAStack` have been removed, since they are
now immutable types. This change is similar to how `list` has a `copy()` method
but `tuple` does not.

## Acceptance mode of PDAs is now configurable

`DPDA` and `NPDA` have a new config option which specifies when to accept. This
can be either `empty_stack`, `final_state` or `both`. The default is `both`.

## Backwards-incompatible changes from v1 to v2

There have been a number of backwards-incompatible changes from Automata v1 to
v2 to clean up the API, including:

### Renames

The following methods and classes have been renamed for better clarity:

#### Shared module

The `automata.shared` package has been renamed to `automata.base`.

**Before:**  
```python
from automata.shared.automaton import Automaton
from automata.shared.exceptions import FinalStateError
```

**After:**  
```python
from automata.base.automaton import Automaton
from automata.base.exceptions import FinalStateError
```

#### Input validation methods

The `validate_input()` method has been renamed to `read_input()`. The
`validate_input(step=True)` form has also been converted to the standalone
method `read_input_stepwise()`.

**Before:**  
```python
final_state = dfa.validate_input('0011')
steps = dfa.validate_input('0011', step=True)
```

**After:**  
```python
final_state = dfa.read_input('0011')
steps = dfa.read_input_stepwise('0011')
```

#### Automaton validation methods

The `validate_self()` method has been renamed to `validate()`.

**Before:**  
```python
dfa.validate_self()
```

**After:**  
```python
dfa.validate()
```

#### Exceptions

The top-level `*Error` exception classes has been renamed to `*Exception`.

**Before:**  
```python
from automata.shared.exceptions import AutomatonError
from automata.shared.exceptions import RejectionError
from automata.pda.exceptions import PDAError
from automata.tm.exceptions import TMError
```

**After:**  
```python
from automata.base.exceptions import AutomatonException
from automata.base.exceptions import RejectionException
from automata.pda.exceptions import PDAException
from automata.tm.exceptions import TMException
```

### Constructor polymorphism removed

In v1, you could copy an automaton (or convert it to another type) by passing it
into the constructor for an Automaton subtype.

#### Copying an automaton

**Before:**  
```python
dfa = DFA(dfa)
```

**After:**  
```python
dfa = dfa.copy()
```

#### Converting NFA to DFA

**Before:**  
```python
dfa = DFA(nfa)
```

**After:**  
```python
dfa = DFA.from_nfa(nfa)
```

#### Converting DFA to NFA

**Before:**  
```python
nfa = NFA(dfa)
```

**After:**  
```python
nfa = NFA.from_dfa(dfa)
```
