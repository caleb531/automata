# class DTM(TM)

[TM Class](class-tm.md)  
[Table of Contents](../README.md)

The `DTM` class is a subclass of `TM` and represents a deterministic Turing
machine. It can be found under `automata/tm/dtm.py`.

Every DTM has the following (required) properties:

1. `states`: a `set` of the DTM's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the DTM's valid input symbols represented as
strings

3. `tape_symbols`: a `set` of the DTM's valid tape symbols represented as
strings

4. `transitions`: a `dict` consisting of the transitions for each state; each
key is a state name and each value is a `dict` which maps a symbol (the key) to
a state (the value)

5. `initial_state`: the name of the initial state for this DTM

6. `blank_symbol`: a symbol from `tape_symbols` to be used as the blank symbol
for this DTM

7. `final_states`: a `set` of final states for this DTM

```python
from automata.tm.dtm import DTM
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

The direction `N` (for no movement) is also supported.

## DTM.read_input(self, input_str)

Returns a `TMConfiguration`. This is basically a tuple containing the final state the machine stopped on, as well as a
`TMTape` object representing the DTM's internal tape (if the input is accepted).

```python
dtm.read_input('01')  # returns TMConfiguration('q4', TMTape('xy..', '.', 3))
```

Calling `config.print()` will produce a more readable output:

```python
dtm.read_input('01').print()
# q4: xy..
#        ^
```

```python
dtm.read_input('011')  # raises RejectionException
```

## DTM.read_input_stepwise(self, input_str)

Yields sets of `TMConfiguration` objects. Those are basically tuples containing the current state and the current tape as a `TMTape` object.

```python
dtm.read_input_stepwise('01')
# yields:
# TMConfiguration('q0', TMTape('01', '.', 0))
# TMConfiguration('q1', TMTape('x1', '.', 1))
# TMConfiguration('q2', TMTape('xy', '.', 0))
# TMConfiguration('q0', TMTape('xy', '.', 1))
# TMConfiguration('q3', TMTape('xy.', '.', 2))
# TMConfiguration('q4', TMTape('xy..', '.', 3))
```

## DTM.accepts_input(self, input_str)

```python
if dtm.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## DTM.copy(self)

```python
dtm.copy()  # returns deep copy of dtm
```

------

[Next: NTM Class](class-ntm.md)  
[TM Class](class-tm.md)  
[Table of Contents](../README.md)
