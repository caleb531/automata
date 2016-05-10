# Automata

*Copyright 2016 Caleb Evans*  
*Released under the MIT license*

[![Build Status](https://travis-ci.org/caleb531/automata.svg?branch=master)](https://travis-ci.org/caleb531/automata)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=master)](https://coveralls.io/r/caleb531/automata?branch=master)

Automata is a Python 3 library which implements the structures and algorithms I
am learning in my Automata Theory class. The project is still under development,
so the API is not yet stable, nor is the code complete in terms of
functionality.

Automata requires Python 3.4 or newer.

## FA API

### class FA

The `FA` class is an abstract base class from which all finite automata inherit.
As such, it cannot be instantiated on its own; you must use the `DFA` and `NFA`
classes instead (or you may create your own subclass if you're feeling
adventurous). The `FA` class can be found under `automata/FA.py`.

### class DFA

The `DFA` class is a subclass of class `FA` which represents a deterministic
finite FA. The `DFA` class can be found under `automata/dfa.py`.

#### DFA properties

Every DFA instance has the following properties:

1. `states`: a `set` of the DFA's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the DFA's valid input symbols, each of which must
also be represented as a string

3. `transitions`: a `dict` consisting of the transitions for each state. Each
key is a state name and each value is a `dict` which maps a symbol (the key) to
a state (the value).

4. `initial_state`: the name of the initial state for this DFA

5. `final_states`: a `set` of final states for this DFA

All of these properties must be supplied when the DFA is
instantiated (see the examples below).

```python
from automata.dfa import DFA
# DFA which matches all binary strings ending in an odd number of '1's
dfa = DFA(
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
```

Please note that the below DFA code examples reference the above `dfa` object.

#### DFA.validate_input(self, input_str, step=False)

The `validate_input()` method checks whether or not the given string is accepted
by the DFA.

If the string is accepted, the method returns the state the FA stopped on (which
presumably is a valid final state).

```python
dfa.validate_input('01')  # returns 'q1'
```

If the string is rejected by the DFA, the method will raise a `RejectionError`.

```python
dfa.validate_input('011')  # raises RejectionError
```

If you supply the `step` keyword argument with a value of `True`, the method
will return a generator which yields each state reached as the DFA reads
characters from the input string.

```python
list(dfa.validate_input('0111', step=True))
# returns ['q0', 'q0', 'q1', 'q2', 'q1']
```

Note that the first yielded state is always the DFA's initial state (before any
input has been read) and the last yielded state is always the DFA's final state
(after all input has been read). If the string is rejected by the DFA, the
method still raises a `RejectionError`.

#### DFA.validate_self(self)

The `validate_self()` method checks whether the DFA is actually a valid DFA. The
method returns `True` if the DFA is valid; otherwise, it will raise the
appropriate exception (*e.g.* the state transition is missing for a particular
symbol). This method is automatically called when the DFA is initialized, so
it's only really useful if a DFA object is modified after instantiation.

#### Copying a DFA

To create an exact copy of a DFA, simply pass an `DFA` instance into the `DFA`
constructor.

```python
dfa_copy = DFA(dfa)  # returns an exact copy of dfa
```

### class NFA

The `NFA` class is a subclass of class `FA` which represents a nondeterministic
finite FA. The `NFA` class can be found under `automata/nfa.py`.

#### NFA properties

Every NFA contains the same five DFA properties: `state`, `input_symbols`,
`transitions`, `initial_state`, and `final_states`. However, the structure of
the  `transitions` object has been modified slightly to accommodate the fact
that a single state can have more than one transition for the same symbol.
Therefore, instead of mapping a symbol to *one* end state in each sub-dict, each
symbol is mapped to a *set* of end states.

```python
from automata.dfa import DFA
from automata.nfa import NFA
# NFA which matches strings beginning with 'a', ending with 'a', and containing
# no consecutive 'b's
nfa = NFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'a', 'b'},
    transitions={
        'q0': {'a': {'q1'}},
        # Use '' as the key name for empty string (lambda/epsilon) transitions
        'q1': {'a': {'q1'}, '': {'q2'}},
        'q2': {'b': {'q0'}}
    },
    initial_state='q0',
    final_states={'q1'}
)
```

#### NFA.validate_input(self, input_str, step=False)

The `validate_input()` method checks whether or not the given string is accepted
by the NFA.

If the string is accepted, the method returns a `set` of states the FA stopped
on (which presumably contains at least one valid final state).

```python
nfa.validate_input('aba')  # returns {'q1', 'q2'}
```

If the string is rejected by the NFA, the method will raise a `RejectionError`.

```python
nfa.validate_input('abba')  # raises RejectionError
```

If you supply the `step` keyword argument with a value of `True`, the method
will return a generator which yields each set of states reached as the NFA reads
characters from the input string.

```python
list(nfa.validate_input('aba', step=True))
# returns [{'q0'}, {'q1', 'q2'}, {'q0'}, {'q1', 'q2'}]
```

Note that the first yielded set is always the lambda closure of the NFA's
initial state, and the last yielded set always contains the lambda closure of at
least one of the NFA's final states (after all input has been read). If the
string is rejected by the NFA, the method still raises a `RejectionError`.

#### NFA.validate_self(self)

The `validate_self()` method checks whether the NFA is actually a valid NFA. The
method has the same basic behavior and prescribed use case as the
`DFA.validate_self()` method, despite being less restrictive (since NFAs are
naturally less restrictive than DFAs).

#### Converting an NFA to a DFA

To create a DFA that is equivalent to an existing NFA, simply pass the `NFA`
instance to the `DFA` constructor.

```python
dfa = DFA(nfa)  # returns an equivalent DFA
```

#### Copying an NFA

To create an exact copy of an NFA, simply pass an `NFA` instance into the `NFA`
constructor.

```python
nfa_copy = NFA(nfa)  # returns an exact copy of nfa
```

### FA exception classes

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See `automata/FA.py` for these
class definitions.

To reference these exceptions (so as to catch them in a `try..except` block or
whatnot), simply import `automata.fa` however you'd like:

```python
import automata.fa as FA
```

#### class FAError

A base class from which all other FA exceptions inherit.

#### class InvalidStateError

Raised if a state is not a valid state for this FA.

#### class InvalidSymbolError

Raised if a symbol is not a valid symbol for this FA.

#### class MissingTransitionError

Raised if a transition is missing from the transition map for this FA.

#### class RejectionError

Raised if the FA stopped on a non-final state after validating input.

## Turing Machine API

In addition to working with finite automata, this library can also simulate
deterministic Turing machines (DTMs).

### class TM

The `TM` class is an abstract base class from which all turing machines inherit.
As such, it cannot be instantiated on its own; you must use the `DTM` class or
create your own subclass instead. The `TM` class can be found under
`turingmachines/tm.py`.

### class DTM

The `DTM` class is a subclass of class `FA` which represents a deterministic
finite FA. The `DTM` class can be found under `automata/dtm.py`.

#### DTM properties

Every DTM instance has the following properties:

1. `states`: a `set` of the DTM's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the DTM's valid input symbols represented as
strings

3. `tape_symbols`: a `set` of the DTM's valid tape symbols represented as
strings

4. `transitions`: a `dict` consisting of the transitions for each state. Each
key is a state name and each value is a `dict` which maps a symbol (the key) to
a state (the value).

5. `initial_state`: the name of the initial state for this DTM

6. `final_states`: a `set` of final states for this DTM

All of these properties must be supplied when the DTM is instantiated (see the
examples below).

```python
from automata.dtm import DTM
# DTM which matches all strings beginning with '0's, and followed by
# the same number of '1's
dtm = DTM(
    states={'q0', 'q1', 'q2', 'q3', 'q4'},
    input_symbols={'0', '1'},
    tape_symbols={'0', '1', 'x', 'y', '.'},
    transitions={
        'q0': {
            '0': ('q1', 'x', 'R'),
            'y': ('q3', 'y', 'R')
        },
        'q1': {
            '0': ('q1', '0', 'R'),
            '1': ('q2', 'y', 'L'),
            'y': ('q1', 'y', 'R')
        },
        'q2': {
            '0': ('q2', '0', 'L'),
            'x': ('q0', 'x', 'R'),
            'y': ('q2', 'y', 'L')
        },
        'q3': {
            'y': ('q3', 'y', 'R'),
            '.': ('q4', '.', 'R')
        }
    },
    initial_state='q0',
    blank_symbol='.',
    final_states={'q4'}
)
```

Please note that the below DTM code examples reference the above `dtm` object.

#### DTM.validate_input(self, input_str, step=False)

The `validate_input()` method checks whether or not the given string is accepted
by the DTM.

If the string is accepted, the method returns a tuple containing the state the
machine stopped on (which presumably is a valid final state), as well as a
`TMTape` object representing the DTM's internal tape.

```python
dtm.validate_input('01')  # returns ('q4', xy.)
```

If the string is rejected by the DTM, the method will raise a `RejectionError`.

```python
dtm.validate_input('011')  # raises RejectionError
```

If you supply the `step` keyword argument with a value of `True`, the method
will return a generator which yields a tuple containing the current state and
the current tape as a `TMTape` object.

```python
[state, tape.copy() for state, tape in dtm.validate_input('01', step=True)]
# returns [
#   ('q0', 01)
#   ('q1', x1)
#   ('q2', xy)
#   ('q0', xy)
#   ('q3', xy)
#   ('q3', xy.)
# ]
```

Please note that each tuple contains a reference to (not a copy of) the current
`TMTape` object. Therefore, if you wish to store the tape at every step, you
must copy the tape as you iterate over the machine configurations (as shown
above).

Also note that the first yielded state is always the DTM's initial state (before
any input has been read) and the last yielded state is always the DTM's final
state (after all input has been read). If the string is rejected by the DTM, the
method still raises a `RejectionError`.
