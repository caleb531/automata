"""Tests of the postfix conversion and parsing utility functions."""

import unittest
import automata.base.exceptions as exceptions
import automata.regex.postfix as postfix
from automata.regex.lexer import Lexer, Token
from typing import List


class Integer(postfix.Literal):
    def val(self) -> int:
        """It evaluates to its (integer) value."""
        return int(self.text)

class Add(postfix.InfixOperator):
    """Addition."""
    def get_precedence(self) -> int:
        return 10  # Precedence: higher than integers, lower than mult

    def op(self, left: int, right: int) -> int:
        return left + right

class Minus(postfix.InfixOperator):
    """Subtraction."""
    def get_precedence(self) -> int:
        return 10  # Precedence: higher than integers, lower than mult

    def op(self, left: int, right: int) -> int:
        return left - right


class Mult(postfix.InfixOperator):
    """Multiplication."""
    def get_precedence(self) -> int:
        return 20  # Higher precedence than addition/substraction.

    def op(self, left: int, right: int) -> int:
        return left * right

class Divide(postfix.InfixOperator):
    """Division."""
    def get_precedence(self) -> int:
        return 20  # Same precedence than multiplication

    def op(self, left: int, right: int) -> int:
        return left // right


class TestArithmeticParser(unittest.TestCase):
    """Test parsing arithmetic expressions."""

    def test_parse_invalid_token(self) -> None:
        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.parse_postfix_tokens([''])

    def test_nested_parenthesized_expression(self) -> None:
        # Parsing:
        # "( 4 + ( 1 + 2 * 3 * ( 4 + 5 ) + 6 ) ) * 7 + 8"
        tokens: List[Token] = [
            postfix.LeftParen('('),
            Integer('4'),
            Add('+'),
            postfix.LeftParen('('),
            Integer('1'),
            Add('+'),
            Integer('2'),
            Mult('*'),
            Integer('3'),
            Mult('*'),
            postfix.LeftParen('('),
            Integer('4'),
            Add('+'),
            Integer('5'),
            postfix.RightParen(')'),
            Add('+'),
            Integer('6'),
            postfix.RightParen(')'),
            postfix.RightParen(')'),
            Mult('*'),
            Integer('7'),
            Add('+'),
            Integer('8'),
        ]

        postfix_tokens: List[Token] = postfix.tokens_to_postfix(tokens)
        res = postfix.parse_postfix_tokens(postfix_tokens)
        self.assertEqual((4 + (1 + 2 * 3 * (4 + 5) + 6)) * 7 + 8, res)

    def setUp(self):
        self.arithmetic_lexer: Lexer = Lexer()

        self.arithmetic_lexer.register_token(lambda x: postfix.LeftParen(x), r'\(')
        self.arithmetic_lexer.register_token(lambda x: postfix.RightParen(x), r'\)')
        self.arithmetic_lexer.register_token(lambda x: Integer(x), r'[0-9]+')
        self.arithmetic_lexer.register_token(lambda x: Add(x), r'\+')
        self.arithmetic_lexer.register_token(lambda x: Minus(x), r'-')
        self.arithmetic_lexer.register_token(lambda x: Mult(x), r'\*')
        self.arithmetic_lexer.register_token(lambda x: Divide(x), r'/')

    def assert_invalid_ordering(self, regexp):
        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex(regexp))

    def test_expression_invalid_ordering(self):
        statements = ['+6', '+5+', '6/', '1 + 2 - + 3', ')(', '(((2))', '(+5', '6/)']

        for statement in statements:
            self.assert_invalid_ordering(statement)

    def parse(self, tokens: List[Token]) -> int:
        postfix_tokens = postfix.tokens_to_postfix(tokens)
        return postfix.parse_postfix_tokens(postfix_tokens)

    def test_single_number(self) -> None:
        val = self.parse(self.arithmetic_lexer.lex('13'))
        self.assertEqual(13, val)

    def test_negative_number(self) -> None:
        val = self.parse(self.arithmetic_lexer.lex('0-13'))
        self.assertEqual(-13, val)

    def test_simple_mult(self) -> None:
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('2 * 4')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('2 * 2 * 2')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('2 * (2 * 2)')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('(2 * 2) * 2')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('(2 + 2) * 2')))

    def test_precedence(self) -> None:
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('2 * 3 + 2')))
        self.assertEqual(10, self.parse(self.arithmetic_lexer.lex('2 * (3+2)')))

    def test_negative_mult(self) -> None:
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('(0-2) * (0- 4)')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('(0-2) * 2 * (0-2)')))
        self.assertEqual(-5, self.parse(self.arithmetic_lexer.lex('1 + (0-2) * 3')))

    def test_division(self) -> None:
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex('4 / 2')))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex('5 / 2')))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex('6 - 8 / 2')))
        self.assertEqual(3, self.parse(self.arithmetic_lexer.lex('3 * 2 / 2')))
        self.assertEqual(3, self.parse(self.arithmetic_lexer.lex('2 * 3 / 2')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('8 / 2 * 2')))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex('(8 / 2) * 2')))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex('8 / (2 * 2)')))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex('16/4/2')))
