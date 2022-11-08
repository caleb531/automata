# Automata

*Copyright 2016-2022 Caleb Evans*
*Released under the MIT license*

[![tests](https://github.com/caleb531/automata/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/automata/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/automata/badge.svg?branch=main)](https://coveralls.io/r/caleb531/automata?branch=main)

Automata is a Python 3 library which implements the structures and algorithms
for finite automata, pushdown automata, and Turing machines. The library
requires Python 3.7 or newer.

Huge thanks to [@YtvwlD][YtvwlD], [@dengl11][dengl11], [@Tagl][Tagl],
[@lewiuberg][lewiuberg], [@CamiloMartinezM][CamiloMartinezM],
[@abhinavsinha‑adrino][abhinavsinha-adrino], and [@eliotwrobson][eliotwrobson]
for their invaluable code contributions to this project! 🎉

[YtvwlD]: https://github.com/YtvwlD
[dengl11]: https://github.com/dengl11
[Tagl]: https://github.com/Tagl
[lewiuberg]: https://github.com/lewiuberg
[CamiloMartinezM]: https://github.com/CamiloMartinezM
[abhinavsinha-adrino]: https://github.com/abhinavsinha-adrino
[eliotwrobson]: https://github.com/eliotwrobson

## Migrating to v6

If you wish to migrate to Automata v6 from an older version, please follow the
[migration guide][migration].

[migration]: https://github.com/caleb531/automata/blob/main/MIGRATION.md

## Installing

You can install the latest version of Automata via pip:

```sh
pip install automata-lib
```

## API

- [class Automaton](#class-automatonmetaclassabcmeta)
  - [Finite Automaton (FA)](#class-faautomaton-metaclassabcmeta)
    - [Deterministic (DFA)](#class-dfafa)
    - [Non-Deterministic (NFA)](#class-nfafa)
    - [Generalized Non-Deterministic (GNFA)](#class-gnfanfa)
  - [Pushdown Automaton (PDA)](#class-pdaautomaton-metaclassabcmeta)
    - [Deterministic (DPDA)](#class-dpdapda)
    - [Non-Deterministic (NPDA)](#class-npdapda)
  - [Turing Machine (TM)](#class-tmautomaton-metaclassabcmeta)
    - [Deterministic (DTM)](#class-dtmtm)
    - [Non-Deterministic (NTM)](#class-ntmtm)
    - [Multi-Tape Non-Deterministic (MNTM)](#class-mntmtm)
- [Regular Expressions](#regular-expressions)
- [Base exception classes](#base-exception-classes)
- [Turing machine exceptions](#turing-machine-exception-classes)

### class Automaton(metaclass=ABCMeta)

The `Automaton` class is an abstract base class from which all automata
(including Turing machines) inherit. As such, it cannot be instantiated on its
own; you must use a defined subclass instead (or you may create your own
subclass if you're feeling adventurous). The `Automaton` class can be found
under `automata/base/automaton.py`.

If you wish to subclass `Automaton`, you can import it like so:

```python
from automata.base.automaton import Automaton
```

The following methods are common to all Automaton subtypes, and must be
implemented if you create your own subclass:

#### Automaton.read_input(self, input_str)

Reads an input string into the automaton, returning the automaton's final
configuration (according to its subtype). If the input is rejected, the method
raises a `RejectionException`.

#### Automaton.read_input_stepwise(self, input_str)

Reads an input string like `read_input()`, except instead of returning the final
configuration, the method returns a generator. The values yielded by this
generator depend on the automaton's subtype.

If the string is rejected by the automaton, the method still raises a
`RejectionException`.

#### Automaton.accepts_input(self, input_str)

Reads an input string like `read_input()`, except it returns a boolean instead
of returning the automaton's final configuration (or raising an exception).
That is, the method always returns `True` if the input is accepted, and it
always returns `False` if the input is rejected. Alternatively, you can use the
`in` keyword such as `word in automaton` to check whether the input is
acccepted.

```python
word in automaton
automaton.accepts_input(word)
```

#### Automaton.copy(self)

Returns a deep copy of the automaton according to its subtype.

### Disabling automatic validation

By default, all Automaton instances are checked for common inconsistencies when
they are instantiated. If inconsistencies are found, the appropriate exception
from `automata.base.exceptions` is raised.

Because this validation can be performance-intensive for large automaton
instances with many states/transitions, you can disable the automatic validation
using the global configuration feature (introduced in v7):

```python
import automata.base.config as global_config

global_config.should_validate_automata = False

# The rest of your code...
```

If, at any point, you wish to opt into validation for a specific Automaton instance, you can call the `validate` method:

```python
my_automaton.validate()
```

### class FA(Automaton, metaclass=ABCMeta)

The `FA` class is an abstract base class from which all finite automata inherit.
The `FA` class can be found under `automata/fa/fa.py`.

If you wish to subclass `FA`, you can import it like so:

```python
from automata.fa.fa import FA
```

### class DFA(FA)

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

#### DFA.read_input(self, input_str)

Returns the final state the DFA stopped on, if the input is accepted.

```python
dfa.read_input('01')  # returns 'q1'
```

```python
dfa.read_input('011')  # raises RejectionException
```

#### DFA.read_input_stepwise(self, input_str)

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

#### DFA.accepts_input(self, input_str)

```python
if dfa.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### DFA.copy(self)

```python
dfa.copy()  # returns deep copy of dfa
```

#### DFA.minify(self, retain_names=False)

Creates a minimal DFA which accepts the same inputs as the old one.
Unreachable states are removed and equivalent states are merged.
States are renamed by default.

```python
minimal_dfa = dfa.minify()
minimal_dfa_with_old_names = dfa.minify(retain_names=True)
```

#### DFA Equivalence

Use the `==` operator to check if two DFAs accept the same language. Please
note that both DFAs must have the same input symbols.

```python
dfa1 == dfa2
```

#### DFA.complement(self, retain_names=False, minify=True)

Creates a DFA which accepts an input if and only if the old one does not.
Minifies by default. Unreachable states are always removed.

```python
minimal_complement_dfa = ~dfa
complement_dfa = dfa.complement(minify=False)
```

#### DFA.union(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the union of A and B. Minifies by default.
Unreachable states are always removed.

```python
minimal_union_dfa = dfa | other_dfa
union_dfa = dfa.union(other_dfa, minify=False)
```

#### DFA.intersection(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the intersection of A and B. Minifies by default.
Unreachable states are always removed.

```python
minimal_intersection_dfa = dfa & other_dfa
intersection_dfa = dfa.intersection(other_dfa, minify=False)
```

#### DFA.difference(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the set difference of A and B, often
denoted A \ B or A - B. Minifies by default.
Unreachable states are always removed.

```python
minimal_difference_dfa = dfa - other_dfa
difference_dfa = dfa.difference(other_dfa, minify=False)
```

#### DFA.symmetric_difference(self, other, retain_names=False, minify=True)

Given two DFAs which accept the languages A and B respectively,
creates a DFA which accepts the symmetric difference of A and B.
Minifies by default. Unreachable states are always removed.

```python
minimal_symmetric_difference_dfa = dfa ^ other_dfa
symmetric_difference_dfa = dfa.symmetric_difference(other_dfa, minify=False)
```

#### DFA.issubset(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of the A is a subset of B, False otherwise.

```python
dfa <= other_dfa
dfa.issubset(other_dfa)
```

#### DFA.issuperset(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of the A is a superset of B, False otherwise.

```python
dfa >= other_dfa
dfa.issuperset(other_dfa)
```

#### DFA.isdisjoint(self, other_dfa)

Given two DFAs which accept the languages A and B respectively,
returns True of A and B are disjoint, False otherwise.

```python
dfa.isdisjoint(other_dfa)
```

#### DFA.isempty(self)

Returns `True` if the DFA does not accept any inputs, False otherwise.

```python
dfa.isempty()
```

#### DFA.isfinite(self)

Returns `True` if the DFA accepts a finite language, False otherwise.

```python
dfa.isfinite()
```

#### DFA.random_word(self, k, seed=None)

Returns a uniformly random word of length `k`

```python
dfa.random_word(1000, seed=42)
```

#### DFA.predecessor(self, input_str, strict=True, key=None)

Returns the first string accepted by the DFA that comes before
the input string in lexicographical order.
See `DFA.successors` for more information.

```python
prev_word = dfa.predecessor('0110')
same_word = dfa.predecessor(prev_word, strict=False)
```

#### DFA.predecessors(self, input_str, strict=True, key=None)

Generates all strings that come before the input string
in lexicographical order.
See `DFA.successors` for more information.

```python
# Generates all strings in a language in lexographical order
for word in dfa.predecessors(None):
    print(word)
```

#### DFA.successor(self, input_str, strict=True, key=None)

Returns the first string accepted by the DFA that comes after
the input string in lexicographical order.
See `DFA.successors` for more information.

```python
next_word = dfa.successor('0110')
same_word = dfa.predecessor(next_word, strict=False)
```

#### DFA.successors(self, input_str, strict=True, key=None, reverse=False)

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

#### DFA.minimum_word_length(self)

Returns the length of the shortest word in the language represented by the DFA.

```python
dfa.minimum_word_length()
```

#### DFA.maximum_word_length(self)

Returns the length of the longest word in the language represented by the DFA.
In the case of infinite languages, `float('inf')` is returned.

```python
dfa.maximum_word_length()
```

#### DFA.count_words_of_length(self, k)

Counts words of length `k` accepted by the DFA.

```python
dfa.count_words_of_length(3)
```

#### DFA.words_of_length(self, k)

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

#### DFA.cardinality(self)

Returns the cardinality of the language represented by the DFA.
Note that `len(dfa)` raises a `ValueError` for infinite languages, whereas `DFA.cardinality` will return `float('inf')`.

```python
dfa.cardinality()
len(dfa)
```

#### DFA.from_prefix(cls, input_symbols, prefix, contains=True)

Directly computes the minimal DFA recognizing strings with the
given prefix.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_prefix_nano = DFA.from_prefix({'a', 'n', 'o', 'b'}, 'nano')
avoids_prefix_nano = DFA.from_prefix({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

#### DFA.from_suffix(cls, input_symbols, suffix, contains=True)

Directly computes the minimal DFA recognizing strings with the
given prefix.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_suffix_nano = DFA.from_suffix({'a', 'n', 'o', 'b'}, 'nano')
avoids_suffix_nano = DFA.from_suffix({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

#### DFA.from_substring(cls, input_symbols, substring, contains=True, must_be_suffix=False)

Directly computes the minimal DFA recognizing strings containing the
given substring.
If `contains` is set to `False` then the complement is constructed instead.
If `must_be_suffix` is set to `True`, then the substring must be a suffix instead.

```python
contains_substring_nano = DFA.contains_substring({'a', 'n', 'o', 'b'}, 'nano')
avoids_substring_nano = DFA.contains_substring({'a', 'n', 'o', 'b'}, 'nano', contains=False)
```

#### DFA.from_subsequence(cls, input_symbols, subsequence, contains=True)

Directly computes the minimal DFA recognizing strings containing the
given subsequence.
If `contains` is set to `False` then the complement is constructed instead.

```python
contains_substring_dcba = DFA.contains_subsequence({'a', 'b', 'c', 'd'}, 'dcba')
avoids_substring_dcba = DFA.contains_subsequence({'a', 'b', 'c', 'd'}, 'dcba', contains=False)
```

#### DFA.of_length(cls, input_symbols, min_length=0, max_length=None, symbols_to_count=None)

Directly computes the minimal DFA which accepts all words whose length is between `min_length`
and `max_length`, inclusive. To allow infinitely long words, the value `None` can be
passed in for `max_length`. If `symbols_to_count` is `None` (default behavior), then counts
all symbols. Otherwise, only counts symbols present in the set `symbols_to_count` and
ignores other symbols.

```python
dfa = DFA.of_length({'0', '1'}, min_length=4)
dfa = DFA.of_length({'0', '1'}, min_length=4, max_length=8)
```

#### DFA.count_mod(cls, input_symbol, k, remainders=None, symbols_to_count=None)

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

#### DFA.nth_from_start(cls, input_symbols, symbol, n)

Directly computes the minimal DFA which accepts all words whose `n`-th character from the end is `symbol`, where `n` is a positive integer.

```python
dfa = DFA.nth_from_start({'0', '1'}, '1', 4)
```

#### DFA.nth_from_end(cls, input_symbols, symbol, n)

Directly computes the minimal DFA which accepts all words whose `n`-th character from the end is `symbol`, where `n` is a positive integer.

```python
dfa = DFA.nth_from_end({'0', '1'}, '1', 4)
```

#### DFA.from_nfa(cls, nfa, retain_names=False, minify=True)

Creates a DFA that is equivalent to the given NFA. States are renamed by
default unless `retain_names` is set to `True`. Minifies by default.

```python
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
dfa = DFA.from_nfa(nfa)  # returns an equivalent DFA
```

#### DFA.from_finite_language(cls, input_symbols, language)

Constructs the minimal DFA corresponding to the given finite language and input symbols.

```python
DFA.from_finite_language(
    language={'aa', 'aaa', 'aaba', 'aabbb', 'abaa', 'ababb', 'abbab',
              'baa', 'babb', 'bbaa', 'bbabb', 'bbbab'},
    input_symbols={'a', 'b'})
```

#### DFA.show_diagram(self, path=None)

```python
dfa.show_diagram(path='./dfa1.png')
```

### class NFA(FA)

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

#### NFA.read_input(self, input_str)

Returns a set of final states the FA stopped on, if the input is accepted.

```python
nfa.read_input('aba')  # returns {'q1', 'q2'}
```

```python
nfa.read_input('abba')  # raises RejectionException
```

#### NFA.read_input_stepwise(self, input_str)

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

#### NFA.accepts_input(self, input_str)

```python
if nfa.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### NFA.copy(self)

```python
nfa.copy()  # returns deep copy of nfa
```

#### NFA Equivalence

Use the `==` operator to check if two NFAs accept the same language. Please
note that both NFAs must have the same input symbols.

```python
nfa1 == nfa2
```

#### NFA.reverse(self)

```python
nfa.reverse()
```

```python
reversed(nfa)
```

#### NFA.concatenate(self, other)

```python
nfa1 + nfa2
```

```python
nfa1.concatenate(nfa2)
```

#### NFA.kleene_star(self)

```python
nfa1.kleene_star()
```

#### NFA.union(self, other)

Returns union of two NFAs

```python
new_nfa = nfa1.union(nfa2)
```

```python
new_nfa = nfa1 | nfa2
```

#### NFA.intersection(self, other)

Returns intersection of two NFAs

```python
new_nfa = nfa1.intersection(nfa2)
```

```python
new_nfa = nfa1 & nfa2
```
#### NFA.right_quotient(self, other)

Returns right quotient of self with respect to other.

```python
new_nfa = nfa1.right_quotient(nfa2)
```

#### NFA.left_quotient(self, other)

Returns left quotient of self with respect to other.

```python
new_nfa = nfa1.left_quotient(nfa2)
```

#### NFA.shuffle_product(self, other)

Returns shuffle product of two NFAs. This produces an NFA that accepts all
interleavings of strings in the input NFAs.
See [this article](https://link.springer.com/chapter/10.1007/978-3-031-19685-0_3) for more details.

```python
new_nfa = nfa1.shuffle_product(nfa2)
```

#### NFA.eliminate_lambda(self)

Removes epsilon transitions from the NFA which recognizes the same language.

```python
nfa1.eliminate_lambda()
```
#### NFA.edit_distance(cls, input_symbols, reference_str, max_edit_distance,
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

#### NFA.from_dfa(cls, dfa)

Creates an NFA that is equivalent to the given DFA.

```python
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
nfa = NFA.from_dfa(dfa)  # returns an equivalent NFA
```

#### NFA.from_regex(cls, regex, input_symbols=None)

Returns a new NFA instance from the given regular expression. The
parameter `input_symbols` should be a set of the input symbols to use,
defaults to all non-reserved symbols in the given `regex`.

```python
from automata.fa.nfa import NFA
nfa1 = NFA.from_regex('ab(c|d)*ba?')
nfa2 = NFA.from_regex('aaa*', input_symbols={'a', 'b'})
```

#### Converting NFA to regular expression

Due to circular dependency constraints, there is no method to convert an NFA
directly to a regular expression. However, it can be accomplished by first
converting to a GNFA:

```python
from automata.fa.gnfa import GNFA
GNFA.from_nfa(my_nfa).to_regex()
```

#### NFA.show_diagram(self, path=None)

```python
nfa1.show_diagram(path='./abc.png')
```

### class GNFA(NFA)

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
    `*`, `|`, `?`, `()`. Check [Regular Expressions](#regular-expressions)

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

#### GNFA.from_dfa(self, dfa)

Initialize this GNFA as one equivalent to the given DFA.

```python
from automata.fa.gnfa import GNFA
from automata.fa.dfa import DFA
gnfa = GNFA.from_dfa(dfa) # returns an equivalent GNFA
```

#### GNFA.from_nfa(self, nfa)

Initialize this GNFA as one equivalent to the given NFA.

```python
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA
gnfa = GNFA.from_nfa(nfa) # returns an equivalent GNFA
```

#### GNFA.copy()

Returns a deep copy of GNFA.

```python
gnfa2 = gnfa1.copy()
```

#### GNFA.to_regex(self)

Convert GNFA to regular expression.

```python
gnfa.to_regex() # returns a regular expression (string)
```

#### GNFA.show_diagram(self, path=None, show_None=True):

Writes a visual diagram of the GNFA to an image file.

1. `path`: the path of the image to be saved
2. `show_None`: A boolean indicating when to show or hide `None` transitions; defaults to `True`.

```python
gnfa.show_diagram(path='./gnfa.png', show_None=False)
```

### class PDA(Automaton, metaclass=ABCMeta)

The `PDA` class is an abstract base class from which all pushdown automata
inherit. It can be found under `automata/pda/pda.py`.

### class DPDA(PDA)

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

#### DPDA.read_input(self, input_str)

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

#### DPDA.read_input_stepwise(self, input_str)

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

#### DPDA.accepts_input(self, input_str)

```python
if dpda.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### DPDA.copy(self)

```python
dpda.copy()  # returns deep copy of dpda
```

### class NPDA(PDA)

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

#### NPDA.read_input(self, input_str)

Returns a `set` of `PDAConfiguration`s representing all of the NPDA's configurations.
Each of these is basically a tuple containing the final state the NPDA stopped on,
the remaining input (an empty string) as well as a `PDAStack` object representing the NPDA's stack (if the input is accepted).

```python
npda.read_input("aaaa") # returns {PDAConfiguration('q2', '', PDAStack(('#',)))}
```

```python
npda.read_input('ab')  # raises RejectionException
```

#### NPDA.read_input_stepwise(self, input_str)

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

#### NPDA.accepts_input(self, input_str)

```python
if npda.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### NPDA.copy(self)

```python
npda.copy()  # returns deep copy of npda
```

### class TM(Automaton, metaclass=ABCMeta)

The `TM` class is an abstract base class from which all Turing machines inherit.
It can be found under `automata/tm/tm.py`.

### class DTM(TM)

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

#### DTM.read_input(self, input_str)

Returns a `TMConfiguration`. This is basically a tuple containing the final state the machine stopped on, as well as a
`TMTape` object representing the DTM's internal tape (if the input is accepted).

```python
dtm.read_input('01')  # returns TMConfiguration('q4', TMTape('xy..', 3))
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

#### DTM.read_input_stepwise(self, input_str)

Yields sets of `TMConfiguration` objects. Those are basically tuples containing the current state and the current tape as a `TMTape` object.

```python
dtm.read_input_stepwise('01')
# yields:
# TMConfiguration('q0', TMTape('01', 0))
# TMConfiguration('q1', TMTape('x1', 1))
# TMConfiguration('q2', TMTape('xy', 0))
# TMConfiguration('q0', TMTape('xy', 1))
# TMConfiguration('q3', TMTape('xy.', 2))
# TMConfiguration('q4', TMTape('xy..', 3))
```

#### DTM.accepts_input(self, input_str)

```python
if dtm.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### DTM.copy(self)

```python
dtm.copy()  # returns deep copy of dtm
```

### class NTM(TM)

The `NTM` class is a subclass of `TM` and represents a nondeterministic Turing machine. It can be found under `automata/tm/ntm.py`.

Every NTM has the following (required) properties:

1. `states`: a `set` of the NTM's valid states, each of which must be
represented as a string

2. `input_symbols`: a `set` of the NTM's valid input symbols represented as
strings

3. `tape_symbols`: a `set` of the NTM's valid tape symbols represented as
strings

4. `transitions`: a `dict` consisting of the transitions for each state; each key is a state name and each value is a `dict` which maps a symbol (the key) to a set of states (the values)

5. `initial_state`: the name of the initial state for this NTM

6. `blank_symbol`: a symbol from `tape_symbols` to be used as the blank symbol for this NTM

7. `final_states`: a `set` of final states for this NTM

```python
from automata.tm.ntm import NTM
# NTM which matches all strings beginning with '0's, and followed by
# the same number of '1's
# Note that the nondeterminism is not really used here.
ntm = NTM(
    states={'q0', 'q1', 'q2', 'q3', 'q4'},
    input_symbols={'0', '1'},
    tape_symbols={'0', '1', 'x', 'y', '.'},
    transitions={
        'q0': {
            '0': {('q1', 'x', 'R')},
            'y': {('q3', 'y', 'R')},
        },
        'q1': {
            '0': {('q1', '0', 'R')},
            '1': {('q2', 'y', 'L')},
            'y': {('q1', 'y', 'R')},
        },
        'q2': {
            '0': {('q2', '0', 'L')},
            'x': {('q0', 'x', 'R')},
            'y': {('q2', 'y', 'L')},
        },
        'q3': {
            'y': {('q3', 'y', 'R')},
            '.': {('q4', '.', 'R')},
        }
    },
    initial_state='q0',
    blank_symbol='.',
    final_states={'q4'}
)
```

The direction `'N'` (for no movement) is also supported.

#### NTM.read_input(self, input_str)

Returns a set of `TMConfiguration`s. These are basically tuples containing the final state the machine stopped on, as well as a
`TMTape` object representing the NTM's internal tape (if the input is accepted).

```python
ntm.read_input('01')  # returns {TMConfiguration('q4', TMTape('xy..', 3))}
```

Calling `config.print()` will produce a more readable output:

```python
ntm.read_input('01').pop().print()
# q4: xy..
#        ^
```

```python
ntm.read_input('011')  # raises RejectionException
```

#### NTM.read_input_stepwise(self, input_str)

Yields sets of `TMConfiguration` objects. Those are basically tuples containing the current state and the current tape as a `TMTape` object.

```python
ntm.read_input_stepwise('01')
# yields:
# {TMConfiguration('q0', TMTape('01', 0))}
# {TMConfiguration('q1', TMTape('x1', 1))}
# {TMConfiguration('q2', TMTape('xy', 0))}
# {TMConfiguration('q0', TMTape('xy', 1))}
# {TMConfiguration('q3', TMTape('xy.', 2))}
# {TMConfiguration('q4', TMTape('xy..', 3))}
```

#### NTM.accepts_input(self, input_str)

```python
if ntm.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### NTM.copy(self)

```python
ntm.copy()  # returns deep copy of ntm
```

### class MNTM(TM)

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

#### MNTM.read_input(self, input_str)

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

#### MNTM.read_input_stepwise(self, input_str)

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

#### MNTM.read_input_as_ntm(self, input_str)

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

#### MNTM.accepts_input(self, input_str)

```python
if mntm.accepts_input(my_input_str):
    print('accepted')
else:
    print('rejected')
```

#### MNTM.copy(self)

```python
ntm.copy()  # returns deep copy of ntm
```

### Regular Expressions

A set of tools for working with regular languages. These can be found under
`automata/base/regex.py`

A regular expression with the following operations only are supported in this library:

- `*`: Kleene star operation, language repeated zero or more times. Ex: `a*`,`(ab)*`
- `+`: Kleene plus operation, language repeated one or more times. Ex: `a+`,`(ab)+`
- `?`: Language repeated zero or one time. Ex: `a?`
- Concatenation. Ex: `abcd`
- `|`: Union. Ex: `a|b`
- `&`: Intersection. Ex: `a&b`
- `()`: Grouping.

This is similar to the python RE module but this library does not support any other
special character than given above. All regular languages can be written with these.

Preferably the tools for the same can be imported as:

```python
import automata.regex.regex as re
```

#### automata.regex.regex.validate(regex)

Returns `True` if the regular expression is valid. Otherwise, raise an
`InvalidRegexError`.

```python
re.validate('ab(c|d)*ba?')
```

#### automata.regex.regex.isequal(re1, re2)

Returns `True` if both regular expressions are equivalent.

```python
re.isequal('aa?', 'a|aa')
re.isequal('aa*', 'a+')
```

#### automata.regex.regex.issubset(re1, re2)

Returns `True` if re1 is a subset of re2.

```python
re.issubset('aa?', 'a*')
```

#### automata.regex.regex.issuperset(re1, re2)

Returns `True` if re1 is a subset of re2.

```python
re.issuperset('a*', 'a?')
```

### Base exception classes

The library also includes a number of exception classes to ensure that errors
never pass silently (unless explicitly silenced). See
`automata/base/exceptions.py` for these class definitions.

To reference these exceptions (so as to catch them in a `try..except` block or
whatnot), simply import `automata.base.exceptions` however you'd like:

```python
import automata.base.exceptions as exceptions
```

#### class AutomatonException

A base class from which all other automata exceptions inherit (including finite
automata and Turing machines).

#### class InvalidStateError

Raised if a specified state does not exist within the automaton's `states`
set.

#### class InvalidSymbolError

Raised if a specified symbol does not exist within the automaton's `symbols`
set.

#### class MissingStateError

Raised if a specified transition definition is missing a defined start state.
This error can also be raised if the initial state does not have any transitions
defined.

#### class MissingSymbolError

Raised if a given symbol is missing where it would otherwise be required for
this type of automaton (e.g. the automaton is missing a transition for one of
the listed symbols).

#### class InitialStateError

Raised if the initial state fails to meet some required condition for this type
of automaton (e.g. if the initial state is also a final state, which is
prohibited for Turing machines).

#### class FinalStateError

Raised if a final state fails to meet some required condition for this type of
automaton (e.g. the final state has transitions to other states, which is
prohibited for Turing machines).

#### class RejectionException

Raised if the automaton did not accept the input string after validating (e.g.
the automaton stopped on a non-final state after validating input).

#### class RegexException

A base class for all regular expression related errors.

#### class InvalidRegexError
Raised if the input regular expression is invalid.

#### class SymbolMismatchError
Raised if input symbols don't match between two automata but are expected to (e.g.
in the creation of a product automaton).

### Turing machine exception classes

The `automata.tm` package also includes a module for exceptions specific to
Turing machines. You can reference these exception classes like so:

```python
import automata.tm.exceptions as tm_exceptions
```

#### class TMException

A base class from which all other Turing machine exceptions inherit.

#### class InvalidDirectionError

Raised if a direction specified in this machine's transition map is not a valid
direction (valid directions include `'L'`, `'R'`, and `'N'`).

#### class InconsistentTapesException(TMException):

Raised if the number of tapes defined for the mntm is not consistent with the transitions.

#### class MalformedExtendedTape(TMException):

Raised if the extended tape for simulating a mntm as a ntm is not valid.
