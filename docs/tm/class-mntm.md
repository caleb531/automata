# class MNTM(TM)

[TM Class](class-tm.md)  
[Table of Contents](../README.md)

The `MNTM` class is a subclass of `TM` and represents a multitape (non)deterministic Turing machine. It can be found under `automata/tm/mntm.py`.

Every MNTM has the following (required) properties:

1. `states`: a `set` of the MNTM's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the MNTM's valid input symbols represented as
strings

3. `tape_symbols`: a `set` of the MNTM's valid tape symbols represented as
strings

4. `n_tapes`: an `int` which dictates the number of tapes of this MNTM

4. `transitions`: a `dict` consisting of the transitions for each state; each key is a state name and each value is a `dict` which maps a symbol (the key) to a set of states (the values)

5. `initial_state`: the name of the initial state for this MNTM

6. `blank_symbol`: a symbol from `tape_symbols` to be used as the blank symbol for this MNTM

7. `final_states`: a `set` of final states for this MNTM

```python
from automata.tm.mntm import MNTM
# MNTM which accepts all strings in {0, 1}* and writes all
# 1's from the first tape (input) to the second tape.
self.mntm1 = MNTM(
    states={'q0', 'q1'},
    input_symbols={'0', '1'},
    tape_symbols={'0', '1', '#'},
    n_tapes=2,
    transitions={
        'q0': {
            ('1', '#'): [('q0', (('1', 'R'), ('1', 'R')))],
            ('0', '#'): [('q0', (('0', 'R'), ('#', 'N')))],
            ('#', '#'): [('q1', (('#', 'N'), ('#', 'N')))],
        }
    },
    initial_state='q0',
    blank_symbol='#',
    final_states={'q1'},
)
```

The direction `'N'` (for no movement) is also supported.

## MNTM.read_input(self, input_str)

Returns a set of `MTMConfiguration`s. These are basically tuples containing the final state the machine stopped on, as well as a
list of `TMTape` objects representing the MNTM's internal tape (if the input is accepted).

```python
mntm.read_input('01')  # returns {MTMConfiguration('q1', [TMTape('01#', 2), TMTape('1#', 1)])}
```

Calling `config.print()` will produce a more readable output:

```python
ntm.read_input('01').pop().print()
# q1:
#> Tape 1: 01#
#            ^
#> Tape 2: 1#
#           ^
```

```python
ntm.read_input('2')  # raises RejectionException
```

## MNTM.read_input_stepwise(self, input_str)

Yields sets of `MTMConfiguration` objects. Those are basically tuples containing the current state and the list of `TMTape` objects.

```python
ntm.read_input_stepwise('0111')
# yields:
# {MTMConfiguration('q0', (TMTape('0111', 0), TMTape('#', 0)))}
# {MTMConfiguration('q0', (TMTape('0111', 1), TMTape('#', 0)))}
# {MTMConfiguration('q0', (TMTape('0111', 2), TMTape('1#', 1)))}
# {MTMConfiguration('q0', (TMTape('0111', 3), TMTape('11#', 2)))}
# {MTMConfiguration('q0', (TMTape('0111#', 4), TMTape('111#', 3)))}
# {MTMConfiguration('q1', (TMTape('0111#', 4), TMTape('111#', 3)))}
```

## MNTM.read_input_as_ntm(self, input_str)

Simulates the MNTM as an NTM by using an extended tape consisting of all tapes of the MNTM separated by a `tape_separator_symbol = _` and
`'virtual heads'` for each `'virtual tape'` (which are basically the portions of the extended tape separated by `'_'`). Each `'virtual head'`
corresponds to a special symbol (`original_symbol + '^'`) on the extended tape which denotes where the actual head of that tape would be if
the MNTM was being run as a MNTM and not a NTM. This is the classic algorithm for performing a single-tape simulation of a multi-tape Turing
machine. For more information, visit Sipser's **Introduction to the Theory of Computation** 3rd Edition, Section 3.2.

```python
ntm.read_input_as_ntm('0111')
# yields:
# {TMConfiguration('q0', TMTape('0^111_#^_', 0))}
# {TMConfiguration('q0', TMTape('01^11_#^_', 8))}
# {TMConfiguration('q0', TMTape('011^1_1#^_', 9))}
# {TMConfiguration('q0', TMTape('0111^_11#^_', 10))}
# {TMConfiguration('q0', TMTape('0111#^_111#^_', 12))}
# {TMConfiguration('q1', TMTape('0111#^_111#^_', 12))}
```

## MNTM.accepts_input(self, input_str)

```python
if mntm.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## MNTM.copy(self)

```python
ntm.copy()  # returns deep copy of ntm
```

------

[TM Class](class-tm.md)  
[Table of Contents](../README.md)
