# Teaching example

This example demonstrate how `automata` can be easily used for teaching purpose.
We adopt [this introduction to finite automata](https://www.geeksforgeeks.org/introduction-of-finite-automata/) to show how `automata` can be incorporated into the material.

## Deterministic finite automaton

We start by building and visualizing the deterministic finite automaton in the tutorial, which accepts any string ending in "a".

```python
from automata.fa.dfa import DFA

dfa = DFA(
    states={"q0", "q1"},
    input_symbols={"a", "b"},
    transitions={"q0": {"a": "q1", "b": "q0"}, "q1": {"a": "q1", "b": "q0"}},
    initial_state="q0",
    final_states={"q1"},
)
dfa.show_diagram()
```

To verify whether our automaton is functioning properly, we supply a list of input strings and check if they're accepted by the automaton.

```python
inputs = [
    "a",
    "aa",
    "aaa",
    "aaaaa",
    "ba",
    "bba",
    "bbbaa",
    "aba",
    "abba",
    "aaba",
    "abaa",
    "bb",
    "bbbbb",
    "bab",
    "baab",
    "bbab",
    "babb",
]
for in_str in inputs:
    if dfa.accepts_input(in_str):
        print("Accepted: {}".format(in_str))
    else:
        print("Rejected: {}".format(in_str))
```

## Nondeterministic finite automaton

We then build a nondeterministic finite automaton in the tutorial that's equivalent to the previous one.

```python
from automata.fa.nfa import NFA

nfa = NFA(
    states={"q0", "q1"},
    input_symbols={"a", "b"},
    transitions={"q0": {"a": {"q0", "q1"}, "b": {"q0"}}},
    initial_state="q0",
    final_states={"q1"},
)
nfa.show_diagram()
```

We can verify that they're equivalent by checking with the same list of input strings:

```python
for in_str in inputs:
    if nfa.accepts_input(in_str):
        print("Accepted: {}".format(in_str))
    else:
        print("Rejected: {}".format(in_str))
```