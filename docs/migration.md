# Automata Migration Guide

## Backwards-incompatible changes from v7 to v8

### Dependency Changes

Python 3.7 support has been dropped. Please upgrade to Python 3.9 or later to
use Automata v8.

Diagrams are no longer being generated using `pydot`; this dependency has been
dropped in favor of using the `visual` optional dependency, which will install
`pygraphviz` and `coloraide` used for generating figures. You should install
this optional dependency if you wish to generate figures. This change was to
allow for native support for displaying finite automaton in Jupyter notebooks.
The style of the diagrams has been lifted from the [visual automata] package,
so you should take a look at the diagrams generated and see if they are still
satisfactory.

[visual automata]: https://pypi.org/project/visual-automata/

Other new dependencies have been added, but these will be installed automatically
along with v8 of the package.

### Greater Support for Partial DFAs

There is now greater support for partial DFAs, which included changing the
`DFA.from_nfa()` function to return a partial DFA instead of a complete one.
To obtain a complete DFA, you must now call `DFA.from_nfa().to_complete(trap_state_name)`,
where `trap_state_name` will be used as the name for a trap state if one needs to
be added.

### Type Hints

Type hints have now been added, meaning that code which previously called functions
with incorrect types may not have been flagged. See output from your typechecker
for more information.

### NFA.from_regex default input symbols
The default set of input symbols for `NFA.from_regex` was changed to all ascii letters and digits.
If needing to use a specific set of input symbols, use the `input_symbols` parameter.

## Backwards-incompatible changes from v6 to v7

### Immutable instances

All Automaton instances are now fully immutable to protect against common
pitfalls, such as mutating an automaton to an invalid state after it's already
been validated.

This means that if you wish to make a change to an automaton instance, you must
retrieve its attributes as a dictionary (using the new `input_parameters`
property), make your desired change, then pass those parameters to the relevant
constructor. For example:

```python
from automata.fa.dfa import DFA

dfa1 = DFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q1'}
)
# You can still copy an automaton just fine
dfa2 = dfa.copy()
# If you want to make a change, you must create a new instance; please note
# that dfa2.input_parameters is always a deep copy of the input parameters for
# dfa2 (in other words, mutating dfa2.input_parameters will not actually mutate
# dfa2)
params = dfa2.input_parameters
params['final_states'] = {'q2'}
dfa3 = DFA(**params)
```

### Renamed Regex Module

The `automata.base.regex` module has been renamed to `automata.regex.regex`
alongside the other regular expression-related modules.

### DFA.minify() defaults

The default value of the `retain_names` parameter for `DFA.minify()` has been
corrected from `True` to `False`; the API documentation has always stated that
the default value _should_ be `False`, however the default value in the code was
actually `True`; therefore, the code has been updated to match the documentation
(#59)
 - Since this code correction may break existing developer code, this is labeled
   as a backwards-_incompatible_ change rather than just a mere bugfix

## Backwards-incompatible changes from v5 to v6

Python 3.6 support has been dropped, since it has been end-of-life since
December 2021. Please upgrade to Python 3.7 or later to use Automata v6.

The [networkx][networkx] package has been added as a required dependency, providing
substantial performance improvements for certain DFA/NFA methods, and also
streamlining the code to improve maintainability.

[networkx]: https://pypi.org/project/networkx/

## Backwards-incompatible changes from v4 to v5

Python 3.5 support has been dropped, since it has been end-of-life since
September 2020. Please upgrade to Python 3.6 or later to use Automata v5.

To support the new graph visualization capabilities, `pydot` has been added as a
project dependency. The `pydot` package will be installed when you run `pip install automata-lib`.

## Backwards-incompatible changes from v3 to v4

The only backwards-incompatible change from v3 to v4 is that support for Python
3.4 has been dropped. This is because Python 3.4 has reached end-of-life, and
will no longer receive updates. For more information, please refer to the
[Python 3.4.10 release notes][release-notes].

There have been no API changes from v3 to v4.

[release-notes]: https://www.python.org/downloads/release/python-3410/

## Backwards-incompatible changes from v2 to v3

There have been a number of backwards-incompatible changes from Automata v2 to
v3 to support the new features, including:

### Some types made immutable

The `PDAStack` type is now immutable and hashable; it still represents the
current stack of a PDA.

Likewise, the `TMTape` is now immutable and hashable; it still represents the
tape of a TM and the current cursor position.

### copy() methods removed for (now) immutable types

The `copy` methods on `TMTape` and `PDAStack` have been removed, since they are
now immutable types. This change is similar to how `list` has a `copy()` method
but `tuple` does not.

### Acceptance mode of PDAs is now configurable

`DPDA` and `NPDA` have a new config option which specifies when to accept. This
can be either `'empty_stack'`, `'final_state'` or `'both'`. The default is
`'both'`.

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
