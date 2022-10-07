import re
import abc
from dataclasses import dataclass
from typing import Callable, List, Optional, Set, Tuple, TypeVar, Generic

ResultT = TypeVar('ResultT')
@dataclass
class LexerError(Exception):
    """An exception raised for issues in lexing"""
    message: str
    position: int


class Token(Generic[ResultT], metaclass=abc.ABCMeta):
    """Base class for tokens."""

    __slots__ = ['text']

    text: str

    def __init__(self, text: str) -> None:
        self.text = text

    def get_precedence(self) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"

TokenFactoryT = Callable[[str], Token[ResultT]]

class TokenRegistry(Generic[ResultT]):
    """Holds a bunch of token rules.

    Attributes:
        _tokens ((Token, re) list): the registered tokens.
    """

    __slots__ = ['_tokens']

    def __init__(self) -> None:
        self._tokens = []

    def register(self, token_factory_fn: TokenFactoryT, token_regex: str) -> None:
        """Register a token.

        Args:
            token (Token): the token class to register
            regexp (str): the regexp for that token
        """
        self._tokens.append((token_factory_fn, re.compile(token_regex)))

    def matching_tokens(self, text: str, start: int):
        """Retrieve all token definitions matching the beginning of a text.

        Args:
            text (str): the text to test
            start (int): the position where matches should be searched in the
                string (see re.match(rx, txt, pos))

        Yields:
            (token_class, re.Match): all token class whose regexp matches the
                text, and the related re.Match object.
        """
        res = []

        for token_factory_fn, regexp in self._tokens:
            match = regexp.match(text, pos=start)
            if match:
                res.append((token_factory_fn, match))

        return res

    def get_token(self, text: str, start: int = 0):
        """Retrieve the next token from some text.

        Args:
            text (str): the text from which tokens should be extracted

        Returns:
            (token_kind, token_text): the token kind and its content.
        """
        best_token_match = None
        best_match = None

        for token_factory_fn, match in self.matching_tokens(text, start):
            if best_match and best_match.end() >= match.end():
                continue

            best_token_match = (token_factory_fn, match)
            best_match = match


        return best_token_match

    def __len__(self):
        return len(self._tokens)


class Lexer(Generic[ResultT]):
    """The core lexer.

    From its list of tokens (provided through the TOKENS class attribute or
    overridden in the _tokens method), it will parse the given text, with the
    following rules:
    - For each (token, regexp) pair, try to match the regexp at the beginning
      of the text
    - If this matches, add token_class(match) to the list of tokens and continue
    - Otherwise, if the first character is either ' ' or '\t', skip it
    - Otherwise, raise a LexerError.

    Attributes:
        tokens (Token, re) list: The known tokens, as a (token class, regexp) list.
    """

    __slots__ = ['tokens', 'blank_chars']

    tokens: TokenRegistry[ResultT]
    blank_chars: Set[str]

    def __init__(self, blank_chars: Set[str] = {' ', '\t'}) -> None:
        self.tokens = TokenRegistry()
        self.blank_chars = set(blank_chars)

    def register_token(self, token_factory_fn: TokenFactoryT, token_regex: str) -> None:
        """Register a token class.

        Args:
            token_class (tdparser.Token): the token class to register
            regexp (optional str): the regexp for elements of that token.
                Defaults to the `regexp` attribute of the token class.
        """

        self.tokens.register(token_factory_fn, token_regex)

    def lex(self, text: str) -> List[Token[ResultT]]:
        """Split self.text into a list of tokens.

        Args:
            text (str): text to parse

        Yields:
            Token: the tokens generated from the given text.
        """
        pos = 0
        res = []

        while pos < len(text):
            token_match = self.tokens.get_token(text, start=pos)
            if token_match is not None:
                token_factory_fn, match = token_match
                matched_text = text[match.start():match.end()]
                res.append(token_factory_fn(matched_text))
                pos += len(matched_text)
            elif text[pos] in self.blank_chars:
                pos += 1
            else:
                raise LexerError(f"Invalid character '{text[pos]}' in '{text}'", position=pos)

        return res
