#!/usr/bin/env python3
"""Classes and methods for parsing regexes into NFAs."""

from itertools import zip_longest, count
from automata.regex.lexer import Lexer
from automata.regex.postfix import (
    LeftParen, RightParen, parse_postfix_tokens,
    InfixOperator, PostfixOperator, Literal, tokens_to_postfix, validate_tokens
)


class NFARegexBuilder:
    """Builder class designed for speed in parsing regular expressions into NFAs."""

    __slots__ = ['_transitions', '_initial_state', '_final_states']
    _state_name_counter = count(0)

    def __init__(self, *, transitions, initial_state, final_states):
        """
        Initialize new builder class and remap state names
        """
        state_map = {
            original_state: self.__get_next_state_name()
            for original_state in transitions
        }

        self._initial_state = state_map[initial_state]
        self._final_states = {state_map[state] for state in final_states}

        self._transitions = {
            state_map[start_state]: {
                chr: {state_map[dest_state] for dest_state in dest_set}
                for chr, dest_set in transition.items()
            }
            for start_state, transition in transitions.items()
        }

    @classmethod
    def from_string_literal(cls, literal):
        """
        Initialize this builder accepting only the given string literal
        """
        transitions = {
            i: {chr: {i+1}}
            for i, chr in enumerate(literal)
        }

        final_state = len(literal)
        transitions[final_state] = dict()

        return cls(
            transitions=transitions,
            initial_state=0,
            final_states={final_state}
        )

    def union(self, other):
        """
        Apply the union operation to the NFA represented by this builder and other
        """
        self._transitions.update(other._transitions)

        new_initial_state = self.__get_next_state_name()

        # Add epsilon transitions from new start state to old ones
        self._transitions[new_initial_state] = {
            '': {self._initial_state, other._initial_state}
        }

        self._initial_state = new_initial_state
        self._final_states.update(other._final_states)

    def concatenate(self, other):
        """
        Apply the concatenate operation to the NFA represented by this builder
        and other.
        """
        self._transitions.update(other._transitions)

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).add(other._initial_state)

        self._final_states = other._final_states

    def kleene_star(self):
        """
        Apply the kleene star operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).add(self._initial_state)

        self._initial_state = new_initial_state
        self._final_states.add(new_initial_state)

    def option(self):
        """
        Apply the option operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        self._initial_state = new_initial_state
        self._final_states.add(new_initial_state)

    @classmethod
    def __get_next_state_name(cls):
        return next(cls._state_name_counter)


class UnionToken(InfixOperator):
    """Subclass of infix operator defining the union operator."""

    def get_precedence(self):
        return 1

    def op(self, left, right):
        left.union(right)
        return left


class KleeneToken(PostfixOperator):
    """Subclass of postfix operator defining the kleene star operator."""

    def get_precedence(self):
        return 3

    def op(self, left):
        left.kleene_star()
        return left


class OptionToken(PostfixOperator):
    """Subclass of postfix operator defining the option operator."""

    def get_precedence(self):
        return 3

    def op(self, left):
        left.option()
        return left


class ConcatToken(InfixOperator):
    """Subclass of infix operator defining the concatenation operator."""

    def get_precedence(self):
        return 2

    def op(self, left, right):
        left.concatenate(right)
        return left


class StringToken(Literal):
    """Subclass of literal token defining a string literal."""

    def val(self):
        return NFARegexBuilder.from_string_literal(self.text)


def add_concat_tokens(token_list):
    """Add concat tokens to list of parsed infix tokens."""

    final_token_list = []

    # Pairs of token types to insert concat tokens in between
    concat_pairs = [
        (Literal, Literal),
        (RightParen, LeftParen),
        (RightParen, Literal),
        (Literal, LeftParen),
        (PostfixOperator, Literal),
        (PostfixOperator, LeftParen)
    ]

    for curr_token, next_token in zip_longest(token_list, token_list[1:]):
        final_token_list.append(curr_token)

        if next_token:
            for firstClass, secondClass in concat_pairs:
                if isinstance(curr_token, firstClass) and isinstance(next_token, secondClass):
                    final_token_list.append(ConcatToken('.'))

    return final_token_list


def get_regex_lexer():
    """Get lexer for parsing regular expressions."""
    lexer: Lexer = Lexer()

    lexer.register_token(LeftParen, r'\(')
    lexer.register_token(RightParen, r'\)')
    lexer.register_token(StringToken, r'[A-Za-z0-9]')
    lexer.register_token(UnionToken, r'\|')
    lexer.register_token(ConcatToken, r'\.')
    lexer.register_token(KleeneToken, r'\*')
    lexer.register_token(OptionToken, r'\?')

    return lexer


def parse_regex(regexstr):
    """Return an NFARegexBuilder corresponding to regexstr."""

    if len(regexstr) == 0:
        return NFARegexBuilder.from_string_literal(regexstr)

    lexer = get_regex_lexer()
    lexed_tokens = lexer.lex(regexstr)
    validate_tokens(lexed_tokens)
    tokens_with_concats = add_concat_tokens(lexed_tokens)
    postfix = tokens_to_postfix(tokens_with_concats)

    return parse_postfix_tokens(postfix)
