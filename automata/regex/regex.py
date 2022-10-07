#!/usr/bin/env python3
"""Methods for working with regular expressions"""

import automata.base.exceptions as exceptions
from automata.regex.parser import get_regex_lexer, validate_tokens
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


def _validate(regex):
    """Return True if the regular expression is valid"""

    try:
        validate_tokens(get_regex_lexer().lex(regex))
    except exceptions.InvalidRegexError:
        return False

    return True

def validate(regex):
    """Raise an error if the regular expression is invalid"""

    if not _validate(regex):
        raise exceptions.InvalidRegexError(
            '{} is an invalid regular expression'.format(
                regex))
    return True


def isequal(re1, re2):
    """Return True if both regular expressions are equivalent"""

    nfa1 = NFA.from_regex(re1)
    nfa2 = NFA.from_regex(re2)
    dfa1 = DFA.from_nfa(nfa1)
    dfa2 = DFA.from_nfa(nfa2)

    return dfa1 == dfa2


def issubset(re1, re2):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1)
    nfa2 = NFA.from_regex(re2)
    dfa1 = DFA.from_nfa(nfa1).minify(retain_names=False)
    dfa2 = DFA.from_nfa(nfa2).minify(retain_names=False)

    return dfa1.issubset(dfa2)


def issuperset(re1, re2):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1)
    nfa2 = NFA.from_regex(re2)
    dfa1 = DFA.from_nfa(nfa1).minify(retain_names=False)
    dfa2 = DFA.from_nfa(nfa2).minify(retain_names=False)

    return dfa2.issubset(dfa1)
