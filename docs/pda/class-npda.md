# class NPDA(PDA)

[PDA Class](class-pda.md)  
[Table of Contents](../index.md)

The `NPDA` class is a subclass of `PDA` and represents a nondeterministic pushdown automaton. It can be found under `automata/pda/npda.py`.

Every NPDA has the following (required) properties:

1. `states`: a `set` of the NPDA's valid states, each of which must be represented as a string

2. `input_symbols`: a `set` of the NPDA's valid input symbols, each of which must also be represented as a string

3. `stack_symbols`: a `set` of the NPDA's valid stack symbols

4. `transitions`: a `dict` consisting of the transitions for each state; see the example below for the exact syntax

5. `initial_state`: the name of the initial state for this NPDA

6. `initial_stack_symbol`: the name of the initial symbol on the stack for this NPDA

7. `final_states`: a `set` of final states for this NPDA

8. `acceptance_mode`: a string defining whether this NPDA accepts by `'final_state'`, `'empty_stack'`, or `'both'`; the default is `'both'`

```python
from automata.pda.npda import NPDA
# NPDA which matches palindromes consisting of 'a's and 'b's
# (accepting by final state)
# q0 reads the first half of the word, q1 the other half, q2 accepts.
# But we have to guess when to switch.
npda = NPDA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'a', 'b'},
    stack_symbols={'A', 'B', '#'},
    transitions={
        'q0': {
            '': {
                '#': {('q2', '#')},
            },
            'a': {
                '#': {('q0', ('A', '#'))},
                'A': {
                    ('q0', ('A', 'A')),
                    ('q1', ''),
                },
                'B': {('q0', ('A', 'B'))},
            },
            'b': {
                '#': {('q0', ('B', '#'))},
                'A': {('q0', ('B', 'A'))},
                'B': {
                    ('q0', ('B', 'B')),
                    ('q1', ''),
                },
            },
        },
        'q1': {
            '': {'#': {('q2', '#')}},
            'a': {'A': {('q1', '')}},
            'b': {'B': {('q1', '')}},
        },
    },
    initial_state='q0',
    initial_stack_symbol='#',
    final_states={'q2'},
    acceptance_mode='final_state'
)
```

## NPDA.read_input(self, input_str)

Returns a `set` of `PDAConfiguration`s representing all of the NPDA's configurations.
Each of these is basically a tuple containing the final state the NPDA stopped on,
the remaining input (an empty string) as well as a `PDAStack` object representing the NPDA's stack (if the input is accepted).

```python
npda.read_input("aaaa") # returns {PDAConfiguration('q2', '', PDAStack(('#',)))}
```

```python
npda.read_input('ab')  # raises RejectionException
```

## NPDA.read_input_stepwise(self, input_str)

Yields `set`s of `PDAConfiguration` object.
Each of these is basically a tuple containing the current state,
the remaining input and the current stack as a `PDAStack` object, if the input is accepted.

```python
npda.read_input_stepwise('aa')
# yields:
# {PDAConfiguration('q0', 'aa', PDAStack(('#',)))}
# {PDAConfiguration('q0', 'a', PDAStack(('#', 'A'))), PDAConfiguration('q2', 'aa', PDAStack(('#',)))}
# {PDAConfiguration('q0', '', PDAStack(('#', 'A', 'A'))), PDAConfiguration('q1', '', PDAStack(('#',)))}
# {PDAConfiguration('q2', '', PDAStack(('#',)))}
```

## NPDA.accepts_input(self, input_str)

```python
if npda.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## NPDA.copy(self)

```python
npda.copy()  # returns deep copy of npda
```

------

[PDA Class](class-pda.md)  
[Table of Contents](../index.md)
