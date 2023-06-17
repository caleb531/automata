# class DFA(FA)

[FA Class](class-fa.md)  
[Table of Contents](../README.md)

The `DFA` class is a subclass of `FA` and represents a deterministic finite
automaton. It can be found under `automata/fa/dfa.py`.

Every DFA has the following (required) properties:

1. `states`: a `set` of the DFA's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the DFA's valid input symbols, each of which must
also be represented as a string

3. `transitions`: a `dict` consisting of the transitions for each state. Each
key is a state name and each value is a `dict` which maps a symbol (the key) to
a state (the value).

4. `initial_state`: the name of the initial state for this DFA

5. `final_states`: a `set` of final states for this DFA

6. `allow_partial`: by default, each DFA state must have a transition to
every input symbol; if `allow_partial` is `True`, you can disable this
characteristic (such that any DFA state can have fewer transitions than input
symbols)

```python
from automata.fa.dfa import DFA
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

## DFA.read_input(self, input_str)

Returns the final state the DFA stopped on, if the input is accepted.

```python
dfa.read_input('01')  # returns 'q1'
```

```python
dfa.read_input('011')  # raises RejectionException
```

## DFA.read_input_stepwise(self, input_str)

Yields each state reached as the DFA reads characters from the input string, if
the input is accepted.

```python
dfa.read_input_stepwise('0111')
# yields:
# 'q0'
# 'q0'
# 'q1'
# 'q2'
# 'q1'
```

## DFA.accepts_input(self, input_str)

```python
if dfa.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

## DFA.copy(self)

```python
dfa.copy()  # returns deep copy of dfa
```

## DFA.minify(self, retain_names=False)

Creates a minimal DFA which accepts the same inputs as the old one.
Unreachable states are removed and equivalent states are merged.
States are renamed by default.

```python
minimal_dfa = dfa.minify()
minimal_dfa_with_old_names = dfa.minify(retain_names=True)
```

## DFA Equivalence

Use the `==` operator to check if two DFAs accept the same language. Please
note that both DFAs must have the same input symbols.

```python
dfa1 == dfa2
```

## DFA.complement(self, retain_names=False, minify=True)

Creates a DFA which accepts an input if and only if the old one does not.
Minifies by default. Unreachable states are always removed.

```python
minimal_complement_dfa = ~dfa
complement_dfa = dfa.complement(minify=False)
```

## DFA.union(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the union of A and B. Minifies by default.
Unreachable states are always removed.

```python
minimal_union_dfa = dfa | other_dfa
union_dfa = dfa.union(other_dfa, minify=False)
```

## DFA.intersection(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the intersection of A and B. Minifies by default.
Unreachable states are always removed.

```python
minimal_intersection_dfa = dfa & other_dfa
intersection_dfa = dfa.intersection(other_dfa, minify=False)
```

## DFA.difference(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the set difference of A and B, often
denoted A \ B or A - B. Minifies by default.
Unreachable states are always removed.

```python
minimal_difference_dfa = dfa - other_dfa
difference_dfa = dfa.difference(other_dfa, minify=False)
```

## DFA.symmetric_difference(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the symmetric difference of A and B.
Minifies by default. Unreachable states are always removed.

```python
minimal_symmetric_difference_dfa = dfa ^ other_dfa
symmetric_difference_dfa = dfa.symmetric_difference(other_dfa, minify=False)
```

## DFA.issubset(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of the A is a subset of B, False otherwise.

```python
dfa <= other_dfa
dfa.issubset(other_dfa)
```

## DFA.issuperset(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of the A is a superset of B, False otherwise.

```python
dfa >= other_dfa
dfa.issuperset(other_dfa)
```

## DFA.isdisjoint(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of A and B are disjoint, False otherwise.

```python
dfa.isdisjoint(other_dfa)
```

## DFA.isempty(self)

Returns `True` if the DFA does not accept any inputs, False otherwise.

```python
dfa.isempty()
```

## DFA.isfinite(self)

Returns `True` if the DFA accepts a finite language, False otherwise.

```python
dfa.isfinite()
```

## DFA.random_word(self, k, seed=None)

Returns a uniformly random word of length `k`

```python
dfa.random_word(1000, seed=42)
```

## DFA.predecessor(self, input_str, strict=True, key=None)

Returns the first string accepted by the DFA that comes before
the input string in lexicographical order.
See `DFA.successors` for more information.

```python
prev_word = dfa.predecessor('0110')
same_word = dfa.predecessor(prev_word, strict=False)
```

## DFA.predecessors(self, input_str, strict=True, key=None)

Generates all strings that come before the input string
in lexicographical order.
See `DFA.successors` for more information.

```python
# Generates all strings in a language in lexographical order
for word in dfa.predecessors(None):
    print(word)
```

## DFA.successor(self, input_str, strict=True, key=None)

Returns the first string accepted by the DFA that comes after
the input string in lexicographical order.
See `DFA.successors` for more information.

```python
next_word = dfa.successor('0110')
same_word = dfa.predecessor(next_word, strict=False)
```

## DFA.successors(self, input_str, strict=True, key=None, reverse=False)

Generates all strings that come after the input string
in lexicographical order.
Passing in `None` will generate all words.
If `strict` is set to `False` and `input_str` is accepted by the DFA then
it will be included in the output.
The value of `key` can be set to define a custom lexicographical ordering.
If `reverse` is set to `True` then predecessors will be generated instead.
Predecessors can only be generated for finite languagesnly for finite languages, infinite languages raise a `ValueError`.

```python
# Generates all strings in a language in lexographical order
for word in dfa.successors(None):
    print(word)
```

## DFA.minimum_word_length(self)

Returns the length of the shortest word in the language represented by the DFA.

```python
dfa.minimum_word_length()
```

## DFA.maximum_word_length(self)

Returns the length of the longest word in the language represented by the DFA.
In the case of infinite languages, `None` is returned. In the case of empty
languages, `EmptyLanguageException` is raised.

```python
dfa.maximum_word_length()
```

## DFA.count_words_of_length(self, k)

Counts words of length `k` accepted by the DFA.

```python
dfa.count_words_of_length(3)
```

## DFA.words_of_length(self, k)

Generates words of length `k` accepted by the DFA.

```python
for word in dfa.words_of_length(3):
    print(word)
```

You can also iterate through all words accepted by the DFA.
Be aware that the generator may be infinite.

```python
for word in dfa:
    if len(word) > 10:
        break
    print(word)
```

## DFA.reset_word_cache(self)

Resets the word and count caches. Can be called if too much memory is being used.

```python
dfa.reset_word_cache()
```

## DFA.cardinality(self)

Returns the cardinality of the language represented by the DFA. Raises an
`InfiniteLanguageException` if the language is infinite.

```python
dfa.cardinality()
len(dfa)
```

## DFA.from_prefix(cls, input_symbols, prefix, contains=True)

Directly computes the minimal DFA recognizing strings with the
given prefix.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_prefix_nano = DFA.from_prefix({'a', 'n', 'o', 'b'}, 'nano')
avoids_prefix_nano = DFA.from_prefix({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

## DFA.from_suffix(cls, input_symbols, suffix, contains=True)

Directly computes the minimal DFA recognizing strings with the
given prefix.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_suffix_nano = DFA.from_suffix({'a', 'n', 'o', 'b'}, 'nano')
avoids_suffix_nano = DFA.from_suffix({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

## DFA.from_substring(cls, input_symbols, substring, contains=True, must_be_suffix=False)

Directly computes the minimal DFA recognizing strings containing the
given substring.
If `contains` is set to `False` then the complement is constructed instead.
If `must_be_suffix` is set to `True`, then the substring must be a suffix instead.

```python
contains_substring_nano = DFA.contains_substring({'a', 'n', 'o', 'b'}, 'nano')
avoids_substring_nano = DFA.contains_substring({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

## DFA.from_subsequence(cls, input_symbols, subsequence, contains=True)

Directly computes the minimal DFA recognizing strings containing the
given subsequence.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_substring_dcba = DFA.contains_subsequence({'a', 'b', 'c', 'd'}, 'dcba')
avoids_substring_dcba = DFA.contains_subsequence({'a', 'b', 'c', 'd'}, 'dcba', contains=False)
```

## DFA.of_length(cls, input_symbols, min_length=0, max_length=None, symbols_to_count=None)

Directly computes the minimal DFA which accepts all words whose length is between `min_length`
and `max_length`, inclusive. To allow infinitely long words, the value `None` can be
passed in for `max_length`. If `symbols_to_count` is `None` (default behavior), then counts
all symbols. Otherwise, only counts symbols present in the set `symbols_to_count` and
ignores other symbols.

```python
dfa = DFA.of_length({'0', '1'}, min_length=4)
dfa = DFA.of_length({'0', '1'}, min_length=4, max_length=8)
```

## DFA.count_mod(cls, input_symbol, k, remainders=None, symbols_to_count=None)

Directly computes a DFA that counts given symbols and accepts all strings where
the remainder of division by `k` is in the set of `remainders` given.
The default value of `remainders` is `{0}` and all symbols are counted by default.
If `symbols_to_count` is `None` (default behavior), then counts all symbols.
Otherwise, only counts symbols present in the set `symbols_to_count` and
ignores other symbols.

```python
even_length_strings = DFA.count_mod({'0', '1'}, 2)
odd_number_of_ones = DFA.count_mod({'0', '1'}, 2, remainders={1}, symbols_to_count={'1'})
```

## DFA.universal_language(cls, input_symbols)

Returns a new DFA which accepts all strings formed from the given input symbols.

```python
DFA.universal_language(input_symbols={'a', 'b'})
```

## DFA.empty_language(cls, input_symbols)

Returns a new DFA which rejects all strings formed from the given input symbols.

```python
DFA.empty_language(input_symbols={'a', 'b'})
```

## DFA.nth_from_start(cls, input_symbols, symbol, n)

Directly computes the minimal DFA which accepts all words whose `n`-th character from the end is `symbol`, where `n` is a positive integer.

```python
dfa = DFA.nth_from_start({'0', '1'}, '1', 4)
```

## DFA.nth_from_end(cls, input_symbols, symbol, n)

Directly computes the minimal DFA which accepts all words whose `n`-th character from the end is `symbol`, where `n` is a positive integer.

```python
dfa = DFA.nth_from_end({'0', '1'}, '1', 4)
```

## DFA.from_nfa(cls, nfa, retain_names=False, minify=True)

Creates a DFA that is equivalent to the given NFA. States are renamed by
default unless `retain_names` is set to `True`. Minifies by default.

```python
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
dfa = DFA.from_nfa(nfa)  # returns an equivalent DFA
```

## DFA.from_finite_language(cls, input_symbols, language)

Constructs the minimal DFA corresponding to the given finite language and input symbols.

```python
DFA.from_finite_language(
    language={'aa', 'aaa', 'aaba', 'aabbb', 'abaa', 'ababb', 'abbab',
              'baa', 'babb', 'bbaa', 'bbabb', 'bbbab'},
    input_symbols={'a', 'b'})
```

## DFA.show_diagram(self, path=None)

```python
dfa.show_diagram(path='./dfa1.png')
```

------

[Next: NFA Class](class-nfa.md)  
[FA Class](class-fa.md)  
[Table of Contents](../README.md)
