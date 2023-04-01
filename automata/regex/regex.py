#!/usr/bin/env python3
"""Methods for working with regular expressions"""

import automata.base.exceptions as exceptions
from automata.fa.nfa import NFA
from automata.regex.parser import RESERVED_CHARACTERS, get_regex_lexer, validate_tokens


def _validate(regex):
    """Return True if the regular expression is valid"""

    try:
        validate(regex)
    except exceptions.InvalidRegexError:
        return False

    return True


def validate(regex):
    """Raise an error if the regular expression is invalid"""
    input_symbols = set(regex) - RESERVED_CHARACTERS

    validate_tokens(get_regex_lexer(input_symbols).lex(regex))

    return True


def isequal(re1, re2, *, input_symbols=None):
    """Return True if both regular expressions are equivalent"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1 == nfa2


def issubset(re1, re2, *, input_symbols=None):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa2


def issuperset(re1, re2, *, input_symbols=None):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1, input_symbols=input_symbols)
    nfa2 = NFA.from_regex(re2, input_symbols=input_symbols)

    return nfa1.union(nfa2) == nfa1
