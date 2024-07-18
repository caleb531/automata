#!/usr/bin/env python3
"""
A set of tools for working with regular expressions. Can recognize regular expressions
over the alphabet of unicode characters and subsets of these, excluding blanks.

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
characters other than those given above. All regular languages can be written with
these.
"""

from itertools import count
from typing import AbstractSet, Optional

import automata.base.exceptions as exceptions
from automata.fa.nfa import NFA
from automata.regex.parser import RESERVED_CHARACTERS, get_regex_lexer, validate_tokens


def _validate(regex: str) -> bool:
    """Return True if the regular expression is valid"""

    try:
        validate(regex)
    except exceptions.InvalidRegexError:
        return False

    return True


def validate(regex: str) -> None:
    """
    Raises an exception if the input regular expression is invalid.

    Raises
    ------
    InvalidRegexError
        Raised if the regex given as input is not well defined.
    """
    input_symbols = set(regex) - RESERVED_CHARACTERS

    validate_tokens(get_regex_lexer(input_symbols, count(0)).lex(regex))


def isequal(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """
    Whether both regular expressions are equivalent.

    Parameters
    ----------
    re1 : str
        The first regular expression as a string.
    re2 : str
        The second regular expression as a string.
    input_symbols : Optional[AbstractSet[str]], default: None
        The set of input symbols when doing the comparison. Defaults to
        all ascii letters and digits.

    Returns
    ------
    bool
        Whether the regular expressions are equivalent.
    """

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1 == nfa2


def issubset(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """
    Whether re1 is a subset of re2.

    Parameters
    ----------
    re1 : str
        The first regular expression as a string.
    re2 : str
        The second regular expression as a string.
    input_symbols : Optional[AbstractSet[str]], default: None
        The set of input symbols when doing the comparison. Defaults to
        all ascii letters and digits.

    Returns
    ------
    bool
        True if re1 is a subset of re2.
    """

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa2


def issuperset(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """
    Whether re1 is a superset of re2.

    Parameters
    ----------
    re1 : str
        The first regular expression as a string.
    re2 : str
        The second regular expression as a string.
    input_symbols : Optional[AbstractSet[str]], default: None
        The set of input symbols when doing the comparison. Defaults to
        all ascii letters and digits.

    Returns
    ------
    bool
        True if re1 is a superset of re2.
    """

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa1
