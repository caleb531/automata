# Regular Expressions

[Table of Contents](README.md)

A set of tools for working with regular languages. These can be found under
`automata/base/regex.py`. Can recognize regular expressions consisting of
ascii uppercase characters, ascii lowercase characters, digits, and subsets of these.

A regular expression with the following operations only are supported in this library:

- `*`: Kleene star operation, language repeated zero or more times. Ex: `a*`,`(ab)*`
- `+`: Kleene plus operation, language repeated one or more times. Ex: `a+`,`(ab)+`
- `?`: Language repeated zero or one time. Ex: `a?`
- Concatenation. Ex: `abcd`
- `|`: Union. Ex: `a|b`
- `&`: Intersection. Ex: `a&b`
- `.`: Wildcard. Ex: `a.b`
- `^`: Shuffle. Ex: `a^b`
- `{}`: Quantifiers expressing finite repetitions. Ex: `a{1,2}`,`a{3,}`
- `()`: The empty string.
- `(...)`: Grouping.

This is similar to the Python `re` module, but this library does not support any special
characters other than those given above. All regular languages can be written with these.

Preferably the tools for the same can be imported as:

```python
import automata.regex.regex as re
```

## automata.regex.regex.validate(regex)

Returns `True` if the regular expression is valid. Otherwise, raise an
`InvalidRegexError`.

```python
re.validate('ab(c|d)*ba?')
```

## automata.regex.regex.isequal(re1, re2, input_symbols=None)

Returns `True` if both regular expressions are equivalent. The
parameter `input_symbols` should be a set of the input symbols to use,
defaults to all non-reserved symbols in `re1` and `re2`.

```python
re.isequal('aa?', 'a|aa')
re.isequal('aa*', 'a+')
```

## automata.regex.regex.issubset(re1, re2, input_symbols=None)

Returns `True` if re1 is a subset of re2. The
parameter `input_symbols` should be a set of the input symbols to use,
defaults to all non-reserved symbols in `re1` and `re2`.

```python
re.issubset('aa?', 'a*')
```

## automata.regex.regex.issuperset(re1, re2, input_symbols=None)

Returns `True` if re1 is a subset of re2. The
parameter `input_symbols` should be a set of the input symbols to use,
defaults to all non-reserved symbols in `re1` and `re2`.

```python
re.issuperset('a*', 'a?')
```

------

[Table of Contents](README.md)
