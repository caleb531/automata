# class GNFA(NFA)

[FA Class](class-fa.md)  
[Table of Contents](../README.md)

The `GNFA` class is a subclass of `NFA` and represents a generalized
nondeterministic finite automaton. It can be found under `automata/fa/gnfa.py`.
Its main usage is for conversion of DFAs and NFAs to regular expressions.

Every `GNFA` has the following properties: `states`, `input_symbols`,
`transitions`, `initial_state`, and `final_state`. This is very similar to the
`NFA` signature, except that a `GNFA` has several differences with respect to
`NFA`
- The `initial_state` has transitions going to every other state but no transitions
coming in from any other state.
- There is only a single `final_state`, and it has transitions coming in from every
other state but no transitions going to any other state. Futhermore, the `final_state`
is not the same has `initial_state`.
- Except for `initial_state` and `final_state`, one transition arrow goes from every state to every other
state and also from each state to itself. To accommodate this, transitions can be
regular expressions and `None` also in addition to normal symbols.

`GNFA` is modified with respect to `NFA` in the following parameters:

1. `final_state`: a string (single state).
2. `transitions`: (its structure is changed from `NFA`) a `dict` consisting of the transitions
for each state except `final_state`. Each key is a state name and each value is `dict`
which maps a state (the key) to the transition expression (the value).
    - value: a regular expression (string) consisting of `input_symbols` and the following symbols only:
    `*`, `|`, `?`, `()`. Check [Regular Expressions](../regular-expressions.md)

```python
from automata.fa.gnfa import GNFA
# GNFA which matches strings beginning with 'a', ending with 'a', and containing
# no consecutive 'b's
gnfa = GNFA(
    states={'q_in', 'q_f', 'q0', 'q1', 'q2'},
    input_symbols={'a', 'b'},
    transitions={
        'q0': {'q1': 'a', 'q_f': None, 'q2': None, 'q0': None},
        'q1': {'q1': 'a', 'q2': '', 'q_f': '', 'q0': None},
        'q2': {'q0': 'b', 'q_f': None, 'q2': None, 'q1': None},
        'q_in': {'q0': '', 'q_f': None, 'q2': None, 'q1': None}
    },
    initial_state='q_in',
    final_state='q_f'
)
```

## GNFA.from_dfa(self, dfa)

Initialize this GNFA as one equivalent to the given DFA.

```python
from automata.fa.gnfa import GNFA
from automata.fa.dfa import DFA
gnfa = GNFA.from_dfa(dfa) # returns an equivalent GNFA
```

## GNFA.from_nfa(self, nfa)

Initialize this GNFA as one equivalent to the given NFA.

```python
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
gnfa = GNFA.from_nfa(nfa) # returns an equivalent GNFA
```

## GNFA.copy()

Returns a deep copy of GNFA.

```python
gnfa2 = gnfa1.copy()
```

## GNFA.to_regex(self)

Convert GNFA to regular expression.

```python
gnfa.to_regex() # returns a regular expression (string)
```

## GNFA.show_diagram(self, path=None, show_None=True):

Writes a visual diagram of the GNFA to an image file.

1. `path`: the path of the image to be saved
2. `show_None`: A boolean indicating when to show or hide `None` transitions; defaults to `True`.

```python
gnfa.show_diagram(path='./gnfa.png', show_None=False)
```

------

[FA Class](class-fa.md)  
[Table of Contents](../README.md)
