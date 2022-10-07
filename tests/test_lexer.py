"""Tests for lexer-related code."""

import unittest
from automata.regex.postfix import Token
from automata.regex.postfix import LeftParen, RightParen
from automata.regex.lexer import TokenRegistry, Lexer, LexerError


def register_parens(lexer: Lexer) -> None:
    lexer.register_token(lambda text: LeftParen(text), r'\(')
    lexer.register_token(lambda text: RightParen(text), r'\)')


class TestTokenRegistryTestCase(unittest.TestCase):

    def test_add_token(self) -> None:
        class AToken(Token):
            pass

        class BToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        self.assertEqual(0, len(registry._tokens))

        registry.register(lambda x: AToken(x), r'a+')
        self.assertEqual(1, len(registry._tokens))

        registry.register(lambda x: BToken(x), r'b+')
        self.assertEqual(2, len(registry._tokens))

    def test_get_matches_no_tokens_notext(self) -> None:
        registry: TokenRegistry = TokenRegistry()
        self.assertEqual([], list(registry.matching_tokens('', 0)))

    def test_get_matches_no_tokens_text(self) -> None:
        registry: TokenRegistry = TokenRegistry()
        self.assertEqual([], list(registry.matching_tokens('foo', 0)))

    def test_get_matches_notext(self) -> None:
        class AToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(lambda x: AToken(x), r'a')
        self.assertEqual([], list(registry.matching_tokens('', 0)))

    def test_get_matches(self) -> None:
        class AToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(lambda x: AToken(x), r'a')

        matches = list(registry.matching_tokens('aaa', 0))
        self.assertEqual(1, len(matches))
        self.assertTrue(isinstance(matches[0][0]('a'), AToken))

    def test_multiple_matches(self) -> None:
        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(lambda x: AToken(x), r'a')
        registry.register(lambda x: AAToken(x), r'aa')

        matches = list(registry.matching_tokens('aaa', 0))
        self.assertEqual(2, len(matches))
        self.assertTrue(isinstance(matches[0][0]('a'), AToken))
        self.assertTrue(isinstance(matches[1][0]('aa'), AAToken))

    def test_get_token_multiple(self) -> None:
        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(lambda x: AToken(x), r'a')
        registry.register(lambda x: AAToken(x), r'aa')

        match = registry.get_token('aaa')
        self.assertIsNotNone(match)
        self.assertTrue(isinstance(match[0]('aa'), AAToken))

    def test_get_token_multiple_inverted(self) -> None:
        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        registry: TokenRegistry = TokenRegistry()
        registry.register(lambda x: AToken(x), r'a')
        registry.register(lambda x: AAToken(x), r'aa')

        match = registry.get_token('aaa')
        self.assertIsNotNone(match)
        self.assertTrue(isinstance(match[0]('aa'), AAToken))


class TestGetTokenTestCase(unittest.TestCase):

    def test_token_precedence(self):
        class AToken(Token):
            pass

        with self.assertRaises(NotImplementedError):
            AToken('').get_precedence()

    def test_get_token_no_text(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token('')
        self.assertIsNone(token_match)

    def test_get_token_no_text_no_tokens(self) -> None:
        lexer: Lexer = Lexer()
        token_match = lexer.tokens.get_token('')
        self.assertIsNone(token_match)

    def test_get_token_unmatched(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token('aaa')
        self.assertIsNone(token_match)

    def test_get_token_no_tokens(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token('aaa')
        self.assertIsNone(token_match)

    def test_get_token(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        match = lexer.tokens.get_token('(((')
        self.assertIsNotNone(match)
        token_factory_fn, re_match = match

        self.assertTrue(isinstance(token_factory_fn('('), LeftParen))
        self.assertIsNotNone(re_match)

    def test_get_token_picks_first(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        token_match = lexer.tokens.get_token('aa(((')
        self.assertIsNone(token_match)

    def test_get_token_scans_all_possible_tokens(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        match = lexer.tokens.get_token(')(')
        self.assertIsNotNone(match)
        token_factory_fn, re_match = match

        self.assertTrue(isinstance(token_factory_fn(')'), RightParen))
        self.assertIsNotNone(re_match)

    def test_longest_match(self) -> None:
        lexer: Lexer = Lexer()
        class AToken(Token):
            pass

        class AAToken(Token):
            pass

        lexer.register_token(lambda x: AToken(x), r'a')
        lexer.register_token(lambda x: AAToken(x), r'aa')

        match = lexer.tokens.get_token('aaa')
        self.assertIsNotNone(match)

        token_factory_fn, re_match = match
        self.assertTrue(isinstance(token_factory_fn('aa'), AAToken))


class TestRegisterTokensTestCase(unittest.TestCase):
    """Tests for Lexer.register_token."""

    def test_register_token(self) -> None:
        class AToken(Token):
            pass

        lexer: Lexer = Lexer()
        self.assertEqual(0, len(lexer.tokens))

        lexer.register_token(lambda x: AToken(x), r'a')
        self.assertEqual(1, len(lexer.tokens))

    def test_register_tokens(self) -> None:
        class AToken(Token):
            pass

        class BToken(Token):
            pass

        lexer: Lexer = Lexer()
        self.assertEqual(0, len(lexer.tokens))

        lexer.register_token(lambda x: AToken(x), r'a')
        lexer.register_token(lambda x: BToken(x), r'b')
        self.assertEqual(2, len(lexer.tokens))

        match_a = lexer.tokens.get_token('a')
        self.assertIsNotNone(match_a)
        token_factory_fn_a, re_match_a = match_a

        self.assertTrue(isinstance(token_factory_fn_a('a'), AToken))
        self.assertIsNotNone(re_match_a)

        match_b = lexer.tokens.get_token('b')
        self.assertIsNotNone(match_b)
        token_factory_fn_b, re_match_b = match_b

        self.assertTrue(isinstance(token_factory_fn_b('b'), BToken))
        self.assertIsNotNone(re_match_b)


class TestLexTestCase(unittest.TestCase):

    def test_lex_empty(self) -> None:
        lexer: Lexer = Lexer()
        tokens = lexer.lex('')
        self.assertEqual(0, len(tokens))

    def test_lex_tokens(self) -> None:
        text = '((((((()()()))))))((((((('
        lexer: Lexer = Lexer()
        register_parens(lexer)

        tokens = lexer.lex(text)
        self.assertEqual(len(text), len(tokens))
        for i, token in enumerate(tokens[:-1]):
            self.assertEqual(text[i], token.text)
            if token.text == '(':
                self.assertTrue(isinstance(token, LeftParen))
            else:
                self.assertTrue(isinstance(token, RightParen))

    def test_lex_skips_blank(self) -> None:
        lexer: Lexer = Lexer()
        register_parens(lexer)

        tokens = lexer.lex('  (')
        self.assertEqual(1, len(tokens))
        self.assertEqual('(', tokens[0].text)
        self.assertTrue(isinstance(tokens[0], LeftParen))

    def test_lex_custom_blank_chars(self) -> None:
        lexer: Lexer = Lexer(blank_chars={'a', ' '})
        register_parens(lexer)

        tokens = lexer.lex(' a(')
        self.assertEqual(1, len(tokens))
        self.assertEqual('(', tokens[0].text)
        self.assertTrue(isinstance(tokens[0], LeftParen))

    def test_lex_invalid_char(self) -> None:
        lexer: Lexer = Lexer()
        with self.assertRaises(LexerError) as cm:
            lexer.lex('foo')
        self.assertEqual(cm.exception.position, 0)

    def test_lex_error_position(self) -> None:
        class AToken(Token):
            pass

        lexer: Lexer = Lexer()
        lexer.register_token(lambda x: AToken(x), r'a')

        with self.assertRaises(LexerError) as cm:
            lexer.lex('aaaabaaa')
        self.assertEqual(cm.exception.position, 4)
