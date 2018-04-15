# Automata Migration Guide

*Copyright 2018 Caleb Evans*  
*Released under the MIT license*

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

The `AutomatonError` exception has been renamed to `AutomatonException`. The
`RejectionError` exception has also been renamed to `RejectionException`.

**Before:**  
```python
from automata.shared.exceptions import AutomatonError
from automata.shared.exceptions import RejectionError
```

**After:**  
```python
from automata.base.exceptions import AutomatonException
from automata.base.exceptions import RejectionException
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
