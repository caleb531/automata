# class GNFA(FA)

[FA Class](class-fa.md)  
[Table of Contents](../README.md)

The `GNFA` class is a subclass of `FA` and represents a generalized
nondeterministic finite automaton. It can be found under `automata/fa/gnfa.py`.
Its main usage is for conversion of DFAs and NFAs to regular expressions. Note
that because of this, the `GNFA` doesn't support any binary operators or reading
input (e.g. `read_input_stepwise`). Every GNFA can be rendered natively inside of-
a Jupyter notebook (automatically calling `show_diagram` without any arguments)
if installed with the `visual` optional dependency. Note that `input_str`
cannot be set as an argument to `show_diagram`, as the `GNFA` does not read input.

Every `GNFA` has the following properties: `states`, `input_symbols`,
`transitions`, `initial_state`, and `final_state`. This is very similar to the
`NFA` signature, except that a `GNFA` has several differences with respect to
`NFA`:
- The `initial_state` has transitions going to every other state but no transitions
coming in from any other state.
- There is only a single `final_state`, and it has transitions coming in from every
other state but no transitions going to any other state. Futhermore, the `final_state`
is not the same has `initial_state`.
- Except for `initial_state` and `final_state`, one transition arrow goes from every state to every other
state and also from each state to itself. To accommodate this, transitions can be
regular expressions and `None` also in addition to normal symbols.


`GNFA` is modified with respect to `NFA` in the following parameters:

1. `final_state`: a single state.
2. `transitions`: A `dict` consisting of the transitions
for each state except `final_state`. Each key is a state name and each value is `dict`
which maps a state (the key) to the transition expression (the value).
    - value: a regular expression (string) consisting of `input_symbols` and the following symbols only:
    `*`, `|`, `?`, `()`. This is a subset of the standard [Regular Expressions](../regular-expressions.md).

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

------

[FA Class](class-fa.md)  
[Table of Contents](../README.md)
