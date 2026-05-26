# class GNFA(FA)

The `GNFA` (Generalized Nondeterministic Finite Automaton) class is primarily used for converting DFAs and NFAs to regular expressions using [Kleene's algorithm](https://en.wikipedia.org/wiki/Kleene%27s_algorithm).

## Converting NFA to Regular Expression

To convert an NFA to a regular expression:

```python
from automata.fa.nfa import NFA
from automata.fa.gnfa import GNFA

# Define an NFA
my_nfa = NFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'a', 'b'},
    transitions={
        'q0': {'a': {'q1'}},
        'q1': {'a': {'q1'}, 'b': {'q2'}},
        'q2': {'b': {'q2'}}
    },
    initial_state='q0',
    final_states={'q2'}
)

# Convert to regex
regex = GNFA.from_nfa(my_nfa).to_regex()
print(regex)  # Output: aa*bb*
```

## Converting DFA to Regular Expression

Similarly, to convert a DFA to a regular expression:

```python
from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA

# Define a DFA
my_dfa = DFA(
    states={'q0', 'q1'},
    input_symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q1'}
)

# Convert to regex
regex = GNFA.from_dfa(my_dfa).to_regex()
print(regex)  # Output: (0|1)*1
```

::: automata.fa.gnfa
