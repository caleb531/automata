# Performance Examples

On this page, we give examples of reading large inputs with the library.
We include timing code in these examples to allow for comparisons with
other implementations.

## Edit distance automaton for large dictionaries

This is an extended version of the [edit distance example](../fa-examples#edit-distance-automaton) on a large input. Here, we will
return all words in the given English dictionary within the specified
edit distance to the target word.

```python
# Imports from automata library
import string
import time

import pooch

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

# First, get a set of all the words we'd like to use
word_file = pooch.retrieve(
    url="https://raw.githubusercontent.com/solardiz/wordlists/master/gutenberg-all-lowercase-words.txt",
    known_hash="62be81d8a5cb2dae11b96bdf85568436b137b9c0961340569ca1fca595774788",
)

with open(word_file, "r") as wf:
    word_set = set(wf.read().splitlines())


print(f"Word set size: {len(word_set):,}")

# Create the DFA recognizing all the words we'd like
# NOTE this DFA is minimal by construction
start = time.perf_counter()
input_symbols = set(string.ascii_lowercase)
word_dfa = DFA.from_finite_language(input_symbols, word_set)
end = time.perf_counter()

print(f"Created recognizing DFA in {end-start:4f} seconds.")
print(f"States in DFA: {len(word_dfa.states):,}")

# Create the automaton recognizing words close to our target
# word from an NFA
target_word = "those"
edit_distance = 2

edit_distance_dfa = DFA.from_nfa(
    NFA.edit_distance(
        input_symbols,
        target_word,
        edit_distance,
    )
)

# Finally, take intersection and print results
start = time.perf_counter()
found_words_dfa = word_dfa & edit_distance_dfa
found_words = list(found_words_dfa)
end = time.perf_counter()

print(f"DFA intersection done in {end-start:4f} seconds.")
print(
    f"All words within edit distance {edit_distance} of "
    f'"{target_word}": {found_words}'
)
```

Note that in this example, the DFA construction is taking place
over a relatively large alphabet (26) and with a large number
of words (> 150,000).

## Minimal DFA from large randomized regex

In this example, we minimize the DFA from a large, randomly
generated regular expression.


```python
# Do imports
import random
import time

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

# Define regex parameters
num_clauses = 1_000
clause_size = 50

# Define the input symbols and randomly
# construct the regex
input_symbols = ["0", "1"]
raw_regex = "|".join(
    "".join(random.choices(input_symbols, k=clause_size)) for _ in range(num_clauses)
)

# Convert the regex to NFA
start = time.perf_counter()
regex_nfa = NFA.from_regex(raw_regex)
end = time.perf_counter()
print(
    f"Created equivalent NFA with {len(regex_nfa.states):,} states in {end-start:4f} seconds."
)

# Convert to (minimized) DFA
start = time.perf_counter()
regex_dfa = DFA.from_nfa(regex_nfa, minify=True)
end = time.perf_counter()

# Print timing and other information
print(
    f"Created equivalent minimized DFA with {len(regex_dfa.states):,} states in {end-start:4f} seconds."
)
print(f"Number of words accepted by DFA: {len(regex_dfa):,}.")
print(f"Minimum word length accepted by DFA: {regex_dfa.minimum_word_length():,}.")
print(f"Maximum word length accepted by DFA: {regex_dfa.minimum_word_length():,}.")
```
