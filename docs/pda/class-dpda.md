# class DPDA(PDA)

[PDA Class](class-pda.md)  
[Table of Contents](../README.md)

The `DPDA` class is a subclass of `PDA` and represents a deterministic finite
automaton. It can be found under `automata/pda/dpda.py`.

Every DPDA has the following (required) properties:

1. `states`: a `set` of the DPDA's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the DPDA's valid input symbols, each of which
must also be represented as a string

3. `stack_symbols`: a `set` of the DPDA's valid stack symbols

4. `transitions`: a `dict` consisting of the transitions for each state; see the
example below for the exact syntax

5. `initial_state`: the name of the initial state for this DPDA

6. `initial_stack_symbol`: the name of the initial symbol on the stack for this
DPDA

7. `final_states`: a `set` of final states for this DPDA

8. `acceptance_mode`: a string defining whether this DPDA accepts by `'final_state'`, `'empty_stack'`, or `'both'`; the default is `'both'`

```python
from automata.pda.dpda import DPDA
# DPDA which which matches zero or more 'a's, followed by the same
# number of 'b's (accepting by final state)
dpda = DPDA(
    states={'q0', 'q1', 'q2', 'q3'},
    input_symbols={'a', 'b'},
    stack_symbols={'0', '1'},
    transitions={
        'q0': {
            'a': {'0': ('q1', ('1', '0'))}  # transition pushes '1' to stack
        },
        'q1': {
            'a': {'1': ('q1', ('1', '1'))},
            'b': {'1': ('q2', '')}  # transition pops from stack
        },
        'q2': {
            'b': {'1': ('q2', '')},
            '': {'0': ('q3', ('0',))}  # transition does not change stack
        }
    },
    initial_state='q0',
    initial_stack_symbol='0',
    final_states={'q3'},
    acceptance_mode='final_state'
)
```

## DPDA.read_input(self, input_str)

Returns a `PDAConfiguration` object representing the DPDA's config.
This is basically a tuple containing the final state the DPDA stopped on,
the remaining input (an empty string)
as well as a `PDAStack` object representing the DPDA's stack (if the input is accepted).

```python
dpda.read_input('ab')  # returns PDAConfiguration('q3', '', PDAStack(('0',)))
```

```python
dpda.read_input('aab')  # raises RejectionException
```

## DPDA.read_input_stepwise(self, input_str)

Yields sets of `PDAConfiguration` objects.
These are basically tuples containing the current state,
the remaining input and the current stack as a `PDAStack` object, if the input is accepted.

```python
dpda.read_input_stepwise('ab')
# yields:
# PDAConfiguration('q0', 'ab', PDAStack(('0',)))
# PDAConfiguration('q1', 'a', PDAStack(('0', '1')))
# PDAConfiguration('q3', '', PDAStack(('0',)))
```

## DPDA.accepts_input(self, input_str)

```python
if dpda.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## DPDA.copy(self)

```python
dpda.copy()  # returns deep copy of dpda
```

------

[PDA Class](class-pda.md)  
[Table of Contents](../README.md)
