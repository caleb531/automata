#!/usr/bin/env python3
"""
Classes and methods for lexing expressions into lists of tokens.

Adapted from code in the tdparser library: https://github.com/rbarrois/tdparser
"""

import abc
import re
from typing import (
    AbstractSet,
    Callable,
    FrozenSet,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from typing_extensions import Self

import automata.base.exceptions as exceptions

ResultT = TypeVar("ResultT")


class Token(Generic[ResultT], metaclass=abc.ABCMeta):
    """Base class for tokens."""

    __slots__: Tuple[str, ...] = ("text",)

    text: str

    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def from_match(cls: Type[Self], match: re.Match) -> Self:
        return cls(match.group())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


TokenFactoryT = Callable[[re.Match], Token[ResultT]]


class TokenRegistry(Generic[ResultT]):
    """Registry holding token rules."""

    __slots__: Tuple[str, ...] = ("_tokens",)

    _tokens: List[Tuple[TokenFactoryT, re.Pattern]]

    def __init__(self) -> None:
        self._tokens = []

    def register(self, token_factory_fn: TokenFactoryT, token_regex: str) -> None:
        """
        Register a token that can be produced by token_factory_fn (a function
        taking in a regex match and returning the final token) and recognized by the
        token_regex pattern.
        """
        self._tokens.append((token_factory_fn, re.compile(token_regex)))

    def matching_tokens(
        self, text: str, start: int
    ) -> Generator[Tuple[TokenFactoryT, re.Match], None, None]:
        """Retrieve all token definitions matching text starting at start."""

        for token_factory_fn, regexp in self._tokens:
            match = regexp.match(text, pos=start)
            if match:
                yield (token_factory_fn, match)

    def get_token(
        self, text: str, start: int = 0
    ) -> Optional[Tuple[TokenFactoryT, re.Match]]:
        """
        Retrieve the next token from some text. Computes the best match by
        length. Returns None if there is no match in the token registry.
        """
        best_token_match = None
        best_match = None

        for token_factory_fn, match in self.matching_tokens(text, start):
            if not best_match or best_match.end() < match.end():
                best_token_match = (token_factory_fn, match)
                best_match = match

        return best_token_match

    def __len__(self) -> int:
        return len(self._tokens)


class Lexer(Generic[ResultT]):
    """
    The core lexer. First, tokens are registered with their factory functions and regex
    patterns. The lexer can then take in a string and splits it into a list of token
    classes (in infix ordering) matching the regex patterns.
    """

    __slots__: Tuple[str, ...] = ("tokens", "blank_chars")

    tokens: TokenRegistry[ResultT]
    blank_chars: FrozenSet[str]

    def __init__(self, blank_chars: Optional[AbstractSet] = None) -> None:
        self.tokens = TokenRegistry()
        self.blank_chars = (
            frozenset((" ", "\t")) if blank_chars is None else frozenset(blank_chars)
        )

    def register_token(self, token_factory_fn: TokenFactoryT, token_regex: str) -> None:
        """
        Register a token class. The token_factory_fn must taken in a
        match object and return an instance of the desired token, and token_regex
        is used by the lexer to match tokens in the input text.
        """

        self.tokens.register(token_factory_fn, token_regex)

    def lex(self, text: str) -> List[Token[ResultT]]:
        """Split text into a list of tokens in infix notation."""

        pos = 0
        res = []

        while pos < len(text):
            token_match = self.tokens.get_token(text, start=pos)
            if token_match is not None:
                token_factory_fn, match = token_match
                res.append(token_factory_fn(match))
                pos += len(match.group())
            elif text[pos] in self.blank_chars:
                pos += 1
            else:
                raise exceptions.LexerError(
                    f"Invalid character '{text[pos]}' in '{text}'", position=pos
                )

        return res
