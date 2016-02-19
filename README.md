# Automata

*Copyright 2016 Caleb Evans*  
*Released under the MIT license*

[![Build Status](https://travis-ci.org/caleb531/automata.svg?branch=master)](https://travis-ci.org/caleb531/automata)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=master)](https://coveralls.io/r/caleb531/automata?branch=master)

Automata is a Python 3 library which implements the structures and algorithms I
am learning in my Automata Theory class. The project is still under development,
so the API is not yet stable, nor is the code complete in terms of
functionality.

## API

### Properties

Every finite automaton instance has the following properties:

1. `state`: a `set` of the automaton's valid states; all state names are
represented as strings

2. `symbols`: a `set` of the automaton's valid symbols, each of which must also
be represented as strings

3. `transitions`: a `dict` consisting of the transitions for each state. The
structure of this object may differ slightly depending on the subclass's
implementation. See the `DFA` and `NFA` class definitions for details on how I
chose to implement state transitions.

4. `initial_state`: the string name of the initial state for this automaton

5. `final_states`: a `set` of final states for this automaton

All of these properties must be supplied when the automaton subclass is
instantiated (see the examples below).

### Methods

#### validate_input(input_str)

The `validate_input()` method checks whether or not the given string is accepted
by the DFA. If the string is accepted, the method returns the state the
automaton stopped on (which is assumed at this point to be a valid final state).
If the string is rejected by the DFA, the method will raise the appropriate
exception.

### class DFA

A subclass of class `Automata` which represents a deterministic finite
automaton. The `DFA` class can be found under `automata/dfa.py`.

#### Example

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

A subclass of class `Automata` which represents a nondeterministic finite
automaton. The `NFA` class can be found under `automata/nfa.py`.

#### Example

```python
from automata.nfa import NFA
# NFA which matches "a", "aaa", or any string of 'a's where number of
# 'a's is even and greater than zero
nfa = NFA(
    states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9'},
    symbols={'a'},
    transitions={
        'q0': {'a': {'q1', 'q8'}},
        'q1': {'a': {'q2'}, '': {'q6'}},
        'q2': {'a': {'q3'}},
        # Empty string transitions use '' as the key name
        'q3': {'': {'q4'}},
        'q4': {'a': {'q5'}},
        # As with any NFA, each state is not required to have transitions
        'q5': {},
        'q6': {'a': {'q7'}},
        'q7': {},
        'q8': {'a': {'q9'}},
        'q9': {'a': {'q8'}}
    },
    initial_state='q0',
    final_states={'q4', 'q6', 'q9'}
)
nfa.validate_input('aaaaaa') # returns {'q5', 'q7', 'q9'}
nfa.validate_input('aaab') # raises InvalidSymbolError
```

### Exception classes

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See `automata/automaton.py`
for these class definitions.
