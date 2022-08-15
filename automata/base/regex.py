#!/usr/bin/env python3
"""Methods for working with regular expressions"""

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


def _validate(regex):
    """Return True if the regular expression is valid"""

    stack1 = 0
    for i in range(len(regex)):
        if regex[i] == '(':
            stack1 += 1
        elif regex[i] == ')':
            stack1 = stack1 - 1

        if stack1 < 0:
            return False

        if regex[i] == '*':
            if i > 0 and regex[i - 1] in {'(', '|', '*', '?'}:
                return False
            elif i == 0:
                return False

        if regex[i] == '|':
            if i > 1 and regex[i - 1] in {'(', '|'}:
                return False
            elif i < len(regex) - 1 and regex[i + 1] in {')', '|', '*', '?'}:
                return False
            elif i == 0 or i == len(regex) - 1:
                return False

        if regex[i] == '(':
            if i < len(regex) - 1 and regex[i + 1] == ')':
                return False
        if i == 0 and regex[i] == '?':
            return False
    if stack1 != 0:
        return False
    else:
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
    nfa1.eliminate_lambda()
    nfa2.eliminate_lambda()
    dfa1 = DFA.from_nfa(nfa1)
    dfa2 = DFA.from_nfa(nfa2)
    dfa1 = dfa1.minify()
    dfa2 = dfa2.minify()

    return dfa1 == dfa2


def issubset(re1, re2):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1)
    nfa2 = NFA.from_regex(re2)
    dfa1 = DFA.from_nfa(nfa1)
    dfa2 = DFA.from_nfa(nfa2)

    return dfa1.issubset(dfa2)


def issuperset(re1, re2):
    """Return True if re1 is a subset of re2"""

    nfa1 = NFA.from_regex(re1)
    nfa2 = NFA.from_regex(re2)
    dfa1 = DFA.from_nfa(nfa1)
    dfa2 = DFA.from_nfa(nfa2)

    return dfa2.issubset(dfa1)
