"""Tests of the postfix conversion and parsing utility functions."""

import unittest
from typing import List, TypeVar

import automata.base.exceptions as exceptions
import automata.regex.postfix as postfix
from automata.regex.lexer import Lexer, Token

ResultT = TypeVar("ResultT")


class Integer(postfix.Literal[int]):
    def val(self) -> int:
        """It evaluates to its (integer) value."""
        return int(self.text)


class Add(postfix.InfixOperator[int]):
    """Addition."""

    def get_precedence(self) -> int:
        return 10  # Precedence: higher than integers, lower than mult

    def op(self, left: int, right: int) -> int:
        return left + right


class Minus(postfix.InfixOperator[int]):
    """Subtraction."""

    def get_precedence(self) -> int:
        return 10  # Precedence: higher than integers, lower than mult

    def op(self, left: int, right: int) -> int:
        return left - right


class Mult(postfix.InfixOperator[int]):
    """Multiplication."""

    def get_precedence(self) -> int:
        return 20  # Higher precedence than addition/substraction.

    def op(self, left: int, right: int) -> int:
        return left * right


class Divide(postfix.InfixOperator[int]):
    """Division."""

    def get_precedence(self) -> int:
        return 20  # Same precedence than multiplication

    def op(self, left: int, right: int) -> int:
        return left // right


class TestTokens(unittest.TestCase):
    """Test token subclasses for not implemented errors."""

    def test_token_abstract_methods_not_implemented(self) -> None:
        """Should raise NotImplementedError when calling abstract methods."""

        with self.assertRaises(NotImplementedError):
            getattr(postfix.Operator, "get_precedence")(postfix.Operator)

        with self.assertRaises(NotImplementedError):
            getattr(postfix.InfixOperator, "op")(postfix.InfixOperator, None, None)

        with self.assertRaises(NotImplementedError):
            getattr(postfix.PostfixOperator, "op")(postfix.PostfixOperator, None)

        with self.assertRaises(NotImplementedError):
            getattr(postfix.Literal, "val")(postfix.Literal)


class TestArithmeticParser(unittest.TestCase):
    """Test parsing arithmetic expressions."""

    arithmetic_lexer: Lexer

    def test_parse_invalid_token(self) -> None:
        """Test exception for invalid input tokens."""
        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.parse_postfix_tokens([""])  # type: ignore

    def test_nested_parenthesized_expression(self) -> None:
        """Test parsing parenthesized expression."""
        # Parsing:
        # "( 4 + ( 1 + 2 * 3 * ( 4 + 5 ) + 6 ) ) * 7 + 8"
        tokens = [
            postfix.LeftParen("("),
            Integer("4"),
            Add("+"),
            postfix.LeftParen("("),
            Integer("1"),
            Add("+"),
            Integer("2"),
            Mult("*"),
            Integer("3"),
            Mult("*"),
            postfix.LeftParen("("),
            Integer("4"),
            Add("+"),
            Integer("5"),
            postfix.RightParen(")"),
            Add("+"),
            Integer("6"),
            postfix.RightParen(")"),
            postfix.RightParen(")"),
            Mult("*"),
            Integer("7"),
            Add("+"),
            Integer("8"),
        ]

        postfix_tokens = postfix.tokens_to_postfix(tokens)
        res = postfix.parse_postfix_tokens(postfix_tokens)
        self.assertEqual((4 + (1 + 2 * 3 * (4 + 5) + 6)) * 7 + 8, res)

    def setUp(self) -> None:
        self.arithmetic_lexer: Lexer = Lexer()

        self.arithmetic_lexer.register_token(postfix.LeftParen.from_match, r"\(")
        self.arithmetic_lexer.register_token(postfix.RightParen.from_match, r"\)")
        self.arithmetic_lexer.register_token(Integer.from_match, r"[0-9]+")
        self.arithmetic_lexer.register_token(Add.from_match, r"\+")
        self.arithmetic_lexer.register_token(Minus.from_match, r"-")
        self.arithmetic_lexer.register_token(Mult.from_match, r"\*")
        self.arithmetic_lexer.register_token(Divide.from_match, r"/")

    def test_expression_invalid_ordering(self) -> None:
        """Check for exception raised when lexing invalid regular expressions."""

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("+6"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("+5+"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("6/"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("1 + 2 - + 3"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex(")("))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("(((2))"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("(+5"))

        with self.assertRaises(exceptions.InvalidRegexError):
            postfix.validate_tokens(self.arithmetic_lexer.lex("6/)"))

    def parse(self, tokens: List[Token[ResultT]]) -> ResultT:
        """Helper function for parsing token list tokens"""
        postfix_tokens = postfix.tokens_to_postfix(tokens)
        return postfix.parse_postfix_tokens(postfix_tokens)

    def test_single_number(self) -> None:
        """Test parsing a single number."""
        val = self.parse(self.arithmetic_lexer.lex("13"))
        self.assertEqual(13, val)

    def test_negative_number(self) -> None:
        """Test parsing a negative number."""
        val = self.parse(self.arithmetic_lexer.lex("0-13"))
        self.assertEqual(-13, val)

    def test_simple_mult(self) -> None:
        """Test parsing simple multiplication."""
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("2 * 4")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("2 * 2 * 2")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("2 * (2 * 2)")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("(2 * 2) * 2")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("(2 + 2) * 2")))

    def test_precedence(self) -> None:
        """Test checking for correct precedence."""
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("2 * 3 + 2")))
        self.assertEqual(10, self.parse(self.arithmetic_lexer.lex("2 * (3+2)")))

    def test_negative_mult(self) -> None:
        """Test multiplying negative numbers."""
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("(0-2) * (0- 4)")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("(0-2) * 2 * (0-2)")))
        self.assertEqual(-5, self.parse(self.arithmetic_lexer.lex("1 + (0-2) * 3")))

    def test_division(self) -> None:
        """Test dividing numbers."""
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex("4 / 2")))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex("5 / 2")))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex("6 - 8 / 2")))
        self.assertEqual(3, self.parse(self.arithmetic_lexer.lex("3 * 2 / 2")))
        self.assertEqual(3, self.parse(self.arithmetic_lexer.lex("2 * 3 / 2")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("8 / 2 * 2")))
        self.assertEqual(8, self.parse(self.arithmetic_lexer.lex("(8 / 2) * 2")))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex("8 / (2 * 2)")))
        self.assertEqual(2, self.parse(self.arithmetic_lexer.lex("16/4/2")))
