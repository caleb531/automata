# class NFA(FA)

[FA Class](class-fa.md)  
[Table of Contents](../README.md)

The `NFA` class is a subclass of `FA` and represents a nondeterministic finite
automaton. It can be found under `automata/fa/nfa.py`.

Every NFA has the same five DFA properties: `state`, `input_symbols`,
`transitions`, `initial_state`, and `final_states`. However, the structure of
the `transitions` object has been modified slightly to accommodate the fact that
a single state can have more than one transition for the same symbol. Therefore,
instead of mapping a symbol to *one* end state in each sub-dict, each symbol is
mapped to a *set* of end states.

```python
from automata.fa.nfa import NFA
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

## NFA.read_input(self, input_str)

Returns a set of final states the FA stopped on, if the input is accepted.

```python
nfa.read_input('aba')  # returns {'q1', 'q2'}
```

```python
nfa.read_input('abba')  # raises RejectionException
```

## NFA.read_input_stepwise(self, input_str)

Yields each set of states reached as the NFA reads characters from the input
string, if the input is accepted.

```python
nfa.read_input_stepwise('aba')
# yields:
# {'q0'}
# {'q1', 'q2'}
# {'q0'}
# {'q1', 'q2'}
```

## NFA.accepts_input(self, input_str)

```python
if nfa.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## NFA.copy(self)

```python
nfa.copy()  # returns deep copy of nfa
```

## NFA Equivalence

Use the `==` operator to check if two NFAs accept the same language. Please
note that both NFAs must have the same input symbols.

```python
nfa1 == nfa2
```

## NFA.reverse(self)

```python
nfa.reverse()
```

```python
reversed(nfa)
```

## NFA.concatenate(self, other)

```python
nfa1 + nfa2
```

```python
nfa1.concatenate(nfa2)
```

## NFA.kleene_star(self)

```python
nfa1.kleene_star()
```

## NFA.union(self, other)

Returns union of two NFAs

```python
new_nfa = nfa1.union(nfa2)
```

```python
new_nfa = nfa1 | nfa2
```

## NFA.intersection(self, other)

Returns intersection of two NFAs

```python
new_nfa = nfa1.intersection(nfa2)
```

```python
new_nfa = nfa1 & nfa2
```
## NFA.right_quotient(self, other)

Returns right quotient of self with respect to other.

```python
new_nfa = nfa1.right_quotient(nfa2)
```

## NFA.left_quotient(self, other)

Returns left quotient of self with respect to other.

```python
new_nfa = nfa1.left_quotient(nfa2)
```

## NFA.shuffle_product(self, other)

Returns shuffle product of two NFAs. This produces an NFA that accepts all
interleavings of strings in the input NFAs.
See [this article](https://link.springer.com/chapter/10.1007/978-3-031-19685-0_3) for more details.

```python
new_nfa = nfa1.shuffle_product(nfa2)
```

## NFA.eliminate_lambda(self)

Removes epsilon transitions from the NFA which recognizes the same language.

```python
nfa1.eliminate_lambda()
```
## NFA.edit_distance(cls, input_symbols, reference_str, max_edit_distance,
insertion=True, deletion=True, substitution=True)

Constructs the NFA for the given reference_str for the given Levenshtein distance.
This NFA recognizes strings within the given Levenshtein distance
(commonly called edit distance) of the reference_str.
Parameters control which error types the NFA will recognize (insertions,
deletions, or substitutions).

If insertion and deletion are False and substitution is True,
then this is the same as Hamming distance.

If insertion and deletion are True and substitution is False,
then this is the same as LCS distance.

insertion, deletion, and substitution all default to True.

```python
levenshtein_nfa = NFA.edit_distance({'0', '1'}, '0101', 2)
hamming_nfa = NFA.edit_distance({'0', '1'}, '0101', 2, insertion=False, deletion=False)
LCS_nfa = NFA.edit_distance({'0', '1'}, '0101', 2, substitution=False)
```

## NFA.from_dfa(cls, dfa)

Creates an NFA that is equivalent to the given DFA.

```python
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
nfa = NFA.from_dfa(dfa)  # returns an equivalent NFA
```

## NFA.from_regex(cls, regex, input_symbols=None)

Returns a new NFA instance from the given regular expression. The
parameter `input_symbols` should be a set of the input symbols to use,
defaults to all non-reserved symbols in the given `regex`.

```python
from automata.fa.nfa import NFA
nfa1 = NFA.from_regex('ab(c|d)*ba?')
nfa2 = NFA.from_regex('aaa*', input_symbols={'a', 'b'})
```

## Converting NFA to regular expression

Due to circular dependency constraints, there is no method to convert an NFA
directly to a regular expression. However, it can be accomplished by first
converting to a GNFA:

```python
from automata.fa.gnfa import GNFA
GNFA.from_nfa(my_nfa).to_regex()
```

## NFA.show_diagram(self, path=None)

```python
nfa1.show_diagram(path='./abc.png')
```

------

[Next: GNFA Class](class-gnfa.md)  
[FA Class](class-fa.md)  
[Table of Contents](../README.md)
