# Regular Expressions

[Table of Contents](index.md)

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

## automata.regex.regex.validate(regex)

Returns `True` if the regular expression is valid. Otherwise, raise an
`InvalidRegexError`.

```python
re.validate('ab(c|d)*ba?')
```

## automata.regex.regex.isequal(re1, re2)

Returns `True` if both regular expressions are equivalent.

```python
re.isequal('aa?', 'a|aa')
re.isequal('aa*', 'a+')
```

## automata.regex.regex.issubset(re1, re2)

Returns `True` if re1 is a subset of re2.

```python
re.issubset('aa?', 'a*')
```

## automata.regex.regex.issuperset(re1, re2)

Returns `True` if re1 is a subset of re2.

```python
re.issuperset('a*', 'a?')
```

------

[Table of Contents](index.md)
