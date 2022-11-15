#!/usr/bin/env python3
"""Classes and methods for converting lists of tokens to postfix ordering."""

import abc
from collections import deque
from itertools import zip_longest

import automata.base.exceptions as exceptions
from automata.regex.lexer import Token


class Operator(Token):
    """Subclass of token defining an operator."""

    @abc.abstractmethod
    def get_precedence(self):
        raise NotImplementedError


class InfixOperator(Operator):
    """Subclass of operator defining an infix operator."""

    @abc.abstractmethod
    def op(self, left, right):
        raise NotImplementedError


class PostfixOperator(Operator):
    """Subclass of operator defining an postfix operator."""

    @abc.abstractmethod
    def op(self, left):
        raise NotImplementedError


class Literal(Token):
    """Subclass of token defining a literal."""

    @abc.abstractmethod
    def val(self):
        raise NotImplementedError


class RightParen(Token):
    """Subclass of token defining a right parenthesis."""

    def __repr__(self):
        return '<)>'


class LeftParen(Token):
    """Subclass of token defining a left parenthesis."""

    def __repr__(self):
        return '<(>'


def validate_tokens(token_list):
    """Validate the inputted tokens list (in infix ordering)."""

    token_list_prev = [None] + token_list

    paren_counter = 0

    for prev_token, curr_token in zip_longest(token_list_prev, token_list):
        # No postfix or infix operators at the beginning
        if prev_token is None and isinstance(curr_token, (InfixOperator, PostfixOperator)):
            raise exceptions.InvalidRegexError(f"'{curr_token}' cannot appear at the start of a statement.")

        # No postfix operators at the end of a statement or right before another operator or right paren
        elif isinstance(prev_token, InfixOperator):
            if curr_token is None:
                raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear at the end of a statement.")
            elif isinstance(curr_token, (InfixOperator, PostfixOperator, RightParen)):
                raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear immediately before '{curr_token}'.")

        # No left parens right before infix or postfix operators, or right before a right paren
        elif isinstance(prev_token, LeftParen):
            if isinstance(curr_token, (InfixOperator, PostfixOperator, RightParen)):
                raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear immediately before '{curr_token}'.")

            # Track open/closed parens
            paren_counter += 1

        elif isinstance(prev_token, RightParen):
            paren_counter -= 1

            if paren_counter < 0:
                raise exceptions.InvalidRegexError("Token list has mismatched parethesis.")

    if paren_counter != 0:
        raise exceptions.InvalidRegexError("Token list has unclosed parethesis.")


def tokens_to_postfix(tokens):
    """Takes in a list of tokens and changes them to postfix ordering."""
    stack = deque()
    res = []

    def comp_precedence(a, b):
        """Compare precedence of operators (two tokens)."""
        return a.get_precedence() <= b.get_precedence()

    for c in tokens:
        if isinstance(c, Literal):
            res.append(c)
        elif isinstance(c, RightParen):
            while len(stack) > 0 and not isinstance(stack[-1], LeftParen):
                res.append(stack.pop())
            stack.pop()
        elif isinstance(c, LeftParen):
            stack.append(c)
        elif not stack or isinstance(stack[-1], LeftParen) or not comp_precedence(c, stack[-1]):
            stack.append(c)
        else:
            while stack and not isinstance(stack[-1], LeftParen) and comp_precedence(c, stack[-1]):
                res.append(stack.pop())
            stack.append(c)

    while stack:
        res.append(stack.pop())

    return res


def parse_postfix_tokens(postfix_tokens):
    """Parse list of postfix tokens to produce value of expression."""

    stack = deque()

    for token in postfix_tokens:
        if isinstance(token, InfixOperator):
            right = stack.pop()
            left = stack.pop()
            stack.append(token.op(left, right))
        elif isinstance(token, PostfixOperator):
            left = stack.pop()
            stack.append(token.op(left))
        elif isinstance(token, Literal):
            stack.append(token.val())
        else:
            raise exceptions.InvalidRegexError(f"Invalid token type {type(token)}")

    return stack[0]
