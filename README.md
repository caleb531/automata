# *Automata*

*Copyright 2016 Caleb Evans*  
*Released under the MIT license*

[![Build Status](https://travis-ci.org/caleb531/automata.svg?branch=master)](https://travis-ci.org/caleb531/automata)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=master)](https://coveralls.io/r/caleb531/automata?branch=master)

*Automata* is a Python 3 library which implements the structures and algorithms I
am learning in my Automata Theory class. The project is still under development,
so the API is not yet stable, nor is the code complete in terms of
functionality.

*Automata* requires Python 3.3 or newer.

## API

### class Automaton

The `Automaton` class is an abstract base class from which all finite automata
inherit. As such, it cannot be instantiated on its own; you must use the `DFA`
and `NFA` classes instead (or you may create your own subclass if you're feeling
adventurous). The `Automaton` class can be found under `automata/automaton.py`.

### class DFA

The `DFA` class is a subclass of class `Automaton` which represents a
deterministic finite automaton. The `DFA` class can be found under
`automata/dfa.py`.

#### DFA properties

Every DFA instance has the following properties:

1. `states`: a `set` of the DFA's valid states, each of which must be
represented as a string

2. `symbols`: a `set` of the DFA's valid symbols, each of which must also be
represented as a string

3. `transitions`: a `dict` consisting of the transitions for each state. Each
key is a state name and each value is a `dict` which maps a symbol (the key) to
a state (the value).

4. `initial_state`: the name of the initial state for this DFA

5. `final_states`: a `set` of final states for this DFA

All of these properties must be supplied when the DFA is
instantiated (see the examples below).

#### Validating input

The `validate_input()` method checks whether or not the given string is accepted
by the DFA. If the string is accepted, the method returns the state the
automaton stopped on (which presumably is a valid final state). If the string is
rejected by the DFA, the method will raise the appropriate exception (see
**Exception classes**).

#### Complete example

```python
from automata.dfa import DFA
# DFA which matches all binary strings ending in an odd number of '1's
dfa = DFA(
    states={'q0', 'q1', 'q2'},
    symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q1'}
)
dfa.validate_input('01') # returns 'q1'
dfa.validate_input('011') # raises FinalStateError
```

### class NFA

The `NFA` class is a subclass of class `Automaton` which represents a
nondeterministic finite automaton. The `NFA` class can be found under
`automata/nfa.py`.

#### NFA properties

Every NFA contains the same five DFA properties: `state`, `symbols`,
`transitions`, `initial_state`, and `final_states`. However, the structure of
the  `transitions` object has been modified slightly to accommodate the fact
that a single state can have more than one transition for the same symbol.
Therefore, instead of mapping a symbol to *one* end state in each sub-dict, each
symbol is mapped to a *set* of end states.

#### Validating input

The `validate_input()` method checks whether or not the given string is accepted
by the NFA. If the string is accepted, the method returns a `set` of states the
automaton stopped on (which presumably contains at least one valid final state).
If the string is rejected by the NFA, the method will raise the appropriate
exception (see **Exception classes**).

#### Converting an NFA to a DFA

The `DFA.from_nfa()` class method creates a DFA that is equivalent to the given
NFA.

#### Complete example

```python
from automata.dfa import DFA
from automata.nfa import NFA
# NFA which matches strings beginning with 'a', ending with 'a', and containing
# no consecutive 'b's
nfa = NFA(
    states={'q0', 'q1', 'q2'},
    symbols={'a', 'b'},
    transitions={
        'q0': {'a': {'q1'}},
        # Use '' as the key name for empty string (lambda) transitions
        'q1': {'a': {'q1'}, '': {'q2'}},
        'q2': {'b': {'q0'}}
    },
    initial_state='q0',
    final_states={'q1'}
)
dfa = DFA.from_nfa(nfa) # returns an equivalent DFA
nfa.validate_input('aba') # returns {'q1', 'q2'}
nfa.validate_input('abba') # raises FinalStateError
```

### Exception classes

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See `automata/automaton.py`
for these class definitions.

To reference these exceptions (so as to catch them in a `try..except` block or
whatnot), simply import `automata.automaton` however you'd like:

```python
import automata.automaton as automaton
```

#### class AutomatonError

A base class from which all other automaton exceptions inherit.

#### class InvalidStateError

Raised if a state is not a valid state for this automaton.

#### class InvalidSymbolError

Raised if a symbol is not a valid symbol for this automaton.

#### class MissingStateError

Raised if a state is missing from the transition map for this automaton.

#### class MissingSymbolError

Raised if a symbol is missing from the transition map for this automaton.

#### class FinalStateError

Raised if the automaton stopped at a non-final state after validating input.
