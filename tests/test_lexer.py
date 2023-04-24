"""Tests for lexer-related code."""

import re
import unittest

import automata.base.exceptions as exceptions
from automata.regex.lexer import Lexer, TokenRegistry
from automata.regex.postfix import LeftParen, RightParen, Token


def register_parens(lexer: Lexer) -> None:
    lexer.register_token(LeftParen.from_match, r"\(")
    lexer.register_token(RightParen.from_match, r"\)")


def make_trivial_match(input_str: str) -> re.Match:
    pattern = re.compile(input_str)
    match_obj = pattern.match(input_str)
    assert match_obj is not None
    return match_obj


class TestTokenRegistryTestCase(unittest.TestCase):
    """Tests for token registry class."""

    def test_add_token(self) -> None:
        """Test adding tokens to registry."""

        class AToken(Token):
            pass

        class BToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        self.assertEqual(0, len(registry._tokens))

        registry.register(AToken.from_match, r"a+")
        self.assertEqual(1, len(registry._tokens))

        registry.register(BToken.from_match, r"b+")
        self.assertEqual(2, len(registry._tokens))

    def test_get_matches_no_tokens_notext(self) -> None:
        """Test for no matching tokens in registry with empty string."""
        registry: TokenRegistry = TokenRegistry()
        self.assertEqual([], list(registry.matching_tokens("", 0)))

    def test_get_matches_no_tokens_text(self) -> None:
        """Test for no matching tokens in registry with text."""
        registry: TokenRegistry = TokenRegistry()
        self.assertEqual([], list(registry.matching_tokens("foo", 0)))

    def test_get_matches_notext(self) -> None:
        """Test for no matches when given a non-empty registry."""

        class AToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(AToken.from_match, r"a")
        self.assertEqual([], list(registry.matching_tokens("", 0)))

    def test_get_matches(self) -> None:
        """Test for matching a single token."""

        class AToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(AToken.from_match, r"a")

        matches = list(registry.matching_tokens("aaa", 0))
        self.assertEqual(1, len(matches))
        self.assertTrue(isinstance(matches[0][0](make_trivial_match("a")), AToken))

    def test_multiple_matches(self) -> None:
        """Test for multiple matches."""

        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(AToken.from_match, r"a")
        registry.register(AAToken.from_match, r"aa")

        matches = list(registry.matching_tokens("aaa", 0))
        self.assertEqual(2, len(matches))
        self.assertTrue(isinstance(matches[0][0](make_trivial_match("a")), AToken))
        self.assertTrue(isinstance(matches[1][0](make_trivial_match("aa")), AAToken))

    def test_get_token_multiple(self) -> None:
        """Test getting best match token."""

        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(AToken.from_match, r"a")
        registry.register(AAToken.from_match, r"aa")

        match = registry.get_token("aaa")

        # Using assert here because mypy doesn't like the unittest methods
        assert match is not None
        self.assertTrue(isinstance(match[0](make_trivial_match("aa")), AAToken))

    def test_get_token_multiple_inverted(self) -> None:
        """Test getting best match token in reverse order"""

        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(AAToken.from_match, r"aa")
        registry.register(AToken.from_match, r"a")

        match = registry.get_token("aaa")
        assert match is not None
        self.assertTrue(isinstance(match[0](make_trivial_match("aa")), AAToken))


class TestGetTokenTestCase(unittest.TestCase):
    """Test token registry in lexer."""

    def test_get_token_no_text(self) -> None:
        """Test getting a token given an empty string."""
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token("")
        self.assertIsNone(token_match)

    def test_get_token_no_text_no_tokens(self) -> None:
        """Test getting a token on an empty string."""
        lexer: Lexer = Lexer()
        token_match = lexer.tokens.get_token("")
        self.assertIsNone(token_match)

    def test_get_token_unmatched(self) -> None:
        """Test getting a token without any in the registry."""
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token("aaa")
        self.assertIsNone(token_match)

    def test_get_token_no_tokens(self) -> None:
        """Test getting a token with an empty registry."""
        lexer: Lexer = Lexer()

        token_match = lexer.tokens.get_token("aaa")
        self.assertIsNone(token_match)

    def test_get_token(self) -> None:
        """Test getting left paren tokens."""
        lexer: Lexer = Lexer()
        register_parens(lexer)

        match = lexer.tokens.get_token("(((")
        assert match is not None
        token_factory_fn, re_match = match

        self.assertTrue(isinstance(token_factory_fn(re_match), LeftParen))
        self.assertIsNotNone(re_match)

    def test_get_token_picks_first(self) -> None:
        """Test that tokens are retrieved from the start."""
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token("aa(((")
        self.assertIsNone(token_match)

    def test_get_token_scans_all_possible_tokens(self) -> None:
        """Test that the lexer scans all tokens in registry."""
        lexer: Lexer = Lexer()
        register_parens(lexer)

        match = lexer.tokens.get_token(")(")
        assert match is not None
        token_factory_fn, re_match = match

        self.assertTrue(isinstance(token_factory_fn(re_match), RightParen))
        self.assertIsNotNone(re_match)

    def test_longest_match(self) -> None:
        """Test that the returned match is the longest one."""

        lexer: Lexer = Lexer()

        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        lexer.register_token(AToken.from_match, r"a")
        lexer.register_token(AAToken.from_match, r"aa")

        match = lexer.tokens.get_token("aaa")
        assert match is not None

        token_factory_fn, re_match = match
        self.assertTrue(isinstance(token_factory_fn(make_trivial_match("aa")), AAToken))


class TestRegisterTokensTestCase(unittest.TestCase):
    """Tests for Lexer.register_token."""

    def test_register_token(self) -> None:
        """Test basic token registration."""

        class AToken(Token):
            pass

        lexer: Lexer = Lexer()
        self.assertEqual(0, len(lexer.tokens))

        lexer.register_token(AToken.from_match, r"a")
        self.assertEqual(1, len(lexer.tokens))

    def test_register_tokens(self) -> None:
        """Test registering multiple tokens."""

        class AToken(Token):
            pass

        class BToken(Token):
            pass

        lexer: Lexer = Lexer()
        self.assertEqual(0, len(lexer.tokens))

        lexer.register_token(AToken.from_match, r"a")
        lexer.register_token(BToken.from_match, r"b")
        self.assertEqual(2, len(lexer.tokens))

        match_a = lexer.tokens.get_token("a")
        assert match_a is not None
        token_factory_fn_a, re_match_a = match_a

        self.assertTrue(isinstance(token_factory_fn_a(make_trivial_match("a")), AToken))
        self.assertIsNotNone(re_match_a)

        match_b = lexer.tokens.get_token("b")
        assert match_b is not None
        token_factory_fn_b, re_match_b = match_b

        self.assertTrue(isinstance(token_factory_fn_b(make_trivial_match("b")), BToken))
        self.assertIsNotNone(re_match_b)


class TestLexTestCase(unittest.TestCase):
    """Tests for the Lexer class."""

    def test_lex_empty(self) -> None:
        """Test lexing an empty string."""
        lexer: Lexer = Lexer()
        tokens = lexer.lex("")
        self.assertEqual(0, len(tokens))

    def test_lex_tokens(self) -> None:
        """Test lexing parenthesis."""

        text = "((((((()()()))))))((((((("
        lexer: Lexer = Lexer()
        register_parens(lexer)

        tokens = lexer.lex(text)
        self.assertEqual(len(text), len(tokens))
        for i, token in enumerate(tokens[:-1]):
            self.assertEqual(text[i], token.text)
            if token.text == "(":
                self.assertTrue(isinstance(token, LeftParen))
            else:
                self.assertTrue(isinstance(token, RightParen))

    def test_lex_skips_blank(self) -> None:
        """Test that the lexer skips blank characters."""

        lexer: Lexer = Lexer()
        register_parens(lexer)

        tokens = lexer.lex("  (")
        self.assertEqual(1, len(tokens))
        self.assertEqual("(", tokens[0].text)
        self.assertTrue(isinstance(tokens[0], LeftParen))

    def test_lex_custom_blank_chars(self) -> None:
        """Test lexing custom blank characters."""

        lexer: Lexer = Lexer(blank_chars={"a", " "})
        register_parens(lexer)

        tokens = lexer.lex(" a(")
        self.assertEqual(1, len(tokens))
        self.assertEqual("(", tokens[0].text)
        self.assertTrue(isinstance(tokens[0], LeftParen))

    def test_lex_invalid_char(self) -> None:
        """Test that the lexer throws an exception on invalid characters."""
        lexer: Lexer = Lexer()
        with self.assertRaises(exceptions.LexerError) as cm:
            lexer.lex("foo")
        self.assertEqual(cm.exception.position, 0)

    def test_lex_error_position(self) -> None:
        """Test the position for the lexer error."""

        class AToken(Token):
            pass

        lexer: Lexer = Lexer()
        lexer.register_token(AToken.from_match, r"a")

        with self.assertRaises(exceptions.LexerError) as cm:
            lexer.lex("aaaabaaa")
        self.assertEqual(cm.exception.position, 4)
