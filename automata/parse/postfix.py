from collections import deque
from itertools import zip_longest
from automata.parse.lexer import Token
import automata.base.exceptions as exceptions
import abc
from typing import Deque, List, Optional, TypeVar

ExpressionResultT = TypeVar('ExpressionResultT')

class Operator(Token[ExpressionResultT]):
    @abc.abstractmethod
    def get_precedence(self) -> int: ...

class InfixOperator(Operator[ExpressionResultT]):
    @abc.abstractmethod
    def op(self, left: ExpressionResultT, right: ExpressionResultT) -> ExpressionResultT: ...

class PostfixOperator(Operator[ExpressionResultT]):
    @abc.abstractmethod
    def op(self, left: ExpressionResultT) -> ExpressionResultT: ...

class Literal(Token[ExpressionResultT]):
    @abc.abstractmethod
    def val(self) -> ExpressionResultT: ...

class RightParen(Token[ExpressionResultT]):
    """A right parenthesis."""

    def __repr__(self) -> str:
        return '<)>'


class LeftParen(Token[ExpressionResultT]):
    """A left parenthesis."""

    def __repr__(self) -> str:
        return '<(>'

def validate_tokens(token_list: List[Token]) -> None:
    "Validate the inputted tokens list."

    token_list_prev: List[Optional[Token]] = [None]
    token_list_prev.extend(token_list)

    paren_counter = 0

    for prev_token, curr_token in zip_longest(token_list_prev, token_list):
        if prev_token is None and (
            isinstance(curr_token, InfixOperator) or isinstance(curr_token, PostfixOperator)
        ):
            raise exceptions.InvalidRegexError(f"Token '{curr_token}' cannot appear at the start of a statement.")

        elif isinstance(prev_token, InfixOperator) and (
            isinstance(curr_token, InfixOperator) or isinstance(curr_token, PostfixOperator)
        ):
            raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear next to '{curr_token}'.")

        elif isinstance(prev_token, InfixOperator):
            if curr_token is None:
                raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear at the end of a statement.")
            elif isinstance(curr_token, RightParen):
                raise exceptions.InvalidRegexError(f"'{prev_token}' cannot appear immediately before ')'.")

        elif isinstance(prev_token, LeftParen):
            if isinstance(curr_token, RightParen):
                raise exceptions.InvalidRegexError("Cannot have right paren immediately after left paren.")
            elif isinstance(curr_token, InfixOperator) or isinstance(curr_token, PostfixOperator):
                raise exceptions.InvalidRegexError(f"'(' cannot appear immediately before '{prev_token}'.")

            paren_counter += 1

        elif isinstance(prev_token, RightParen):
            paren_counter -= 1

            if paren_counter < 0:
                raise exceptions.InvalidRegexError("Token list has mismatched parethesis.")

    if paren_counter != 0:
        raise exceptions.InvalidRegexError("Token list has unclosed parethesis.")



def tokens_to_postfix(tokens: List[Token[ExpressionResultT]]) -> List[Token[ExpressionResultT]]:
    "Takes in tokens and changes them to postfix ordering"
    stk: Deque[Token] = deque()
    res: List[Token] = []

    def comp_precedence(a: Token, b: Token) -> bool:
        "Compare precedence of operators"
        return a.get_precedence() <= b.get_precedence()

    for c in tokens:
        if isinstance(c, Literal) or isinstance(c, PostfixOperator):
            res.append(c)
        elif isinstance(c, RightParen):
            while len(stk) > 0 and not isinstance(stk[-1], LeftParen):
                res.append(stk.pop())
            stk.pop()
        elif isinstance(c, LeftParen):
            stk.append(c)
        elif not stk or isinstance(stk[-1], LeftParen) or not comp_precedence(c, stk[-1]):
            stk.append(c)
        else:
            while stk and not isinstance(stk[-1], LeftParen) and comp_precedence(c, stk[-1]):
                res.append(stk.pop())
            stk.append(c)

    while stk:
        res.append(stk.pop())

    return res


def parse_postfix_tokens(postfix_tokens: List[Token[ExpressionResultT]]) -> ExpressionResultT:
    """Parse list of postfix tokens to produce value of expression"""

    stack: Deque[ExpressionResultT] = deque()

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
