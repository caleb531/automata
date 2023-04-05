#!/usr/bin/env python3
"""Methods for working with regular expressions"""

from itertools import count
from typing import AbstractSet, Literal, Optional

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


def validate(regex: str) -> Literal[True]:
    """Raise an error if the regular expression is invalid"""
    input_symbols = set(regex) - RESERVED_CHARACTERS

    validate_tokens(get_regex_lexer(input_symbols, count(0)).lex(regex))

    return True


def isequal(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """Return True if both regular expressions are equivalent"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1 == nfa2


def issubset(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa2


def issuperset(
    re1: str, re2: str, *, input_symbols: Optional[AbstractSet[str]] = None
) -> bool:
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa1
