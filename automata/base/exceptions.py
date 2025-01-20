"""Exception classes shared by all automata."""

from dataclasses import dataclass


class AutomatonException(Exception):
    """The base class for all automaton-related errors."""

    pass


class InvalidStateError(AutomatonException):
    """A state is not a valid state for this automaton."""

    pass


class InvalidSymbolError(AutomatonException):
    """A symbol is not a valid symbol for this automaton."""

    pass


class MissingStateError(AutomatonException):
    """A state is missing from the automaton definition."""

    pass


class MissingSymbolError(AutomatonException):
    """A symbol is missing from the automaton definition."""

    pass


class InitialStateError(AutomatonException):
    """The initial state fails to meet some required condition."""

    pass


class FinalStateError(AutomatonException):
    """A final state fails to meet some required condition."""

    pass


class RejectionException(AutomatonException):
    """The input was rejected by the automaton."""

    pass


class RegexException(Exception):
    """The base class for all regular expression related errors"""

    pass


@dataclass
class LexerError(RegexException):
    """An exception raised for issues in lexing"""

    message: str
    position: int


class InvalidRegexError(RegexException):
    """Regular expression is invalid"""

    pass


class SymbolMismatchError(AutomatonException):
    """The input symbols between the given automata do not match"""

    pass


class EmptyLanguageException(AutomatonException):
    """The operation cannot be performed because the language is empty"""

    pass


class InfiniteLanguageException(AutomatonException):
    """The operation cannot be performed because the language is infinite"""

    pass


class DiagramException(AutomatonException):
    """The diagram cannot be produced"""

    pass
