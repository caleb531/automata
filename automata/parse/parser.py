from itertools import zip_longest, count
from automata.parse.lexer import Lexer, Token
from automata.parse.postfix import (
    LeftParen, RightParen, parse_postfix_tokens,
    InfixOperator, PostfixOperator, Literal, tokens_to_postfix, validate_tokens
)

from typing import Dict, Set, Type, List

BuilderTransitionsT = Dict[int, Dict[str, Set[int]]]

class NFARegexBuilder:
    __slots__ = ['_transitions', '_initial_state', '_final_states']
    _state_name_counter = count(0)

    _transitions: BuilderTransitionsT
    _initial_state: int
    _final_states: Set[int]

    def __init__(self, *, transitions: BuilderTransitionsT, initial_state: int, final_states: Set[int]) -> None:
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
    def from_dfa(cls: Type['NFARegexBuilder'], dfa) -> 'NFARegexBuilder':
        new_transitions: BuilderTransitionsT = {
            start_state: {
                input_symbol: {end_state}
                for input_symbol, end_state in transition.items()
            }
            for start_state, transition in dfa.transitions.items()
        }

        return cls(
            transitions = new_transitions,
            initial_state = dfa.initial_state,
            final_states = dfa.final_states
        )


    @classmethod
    def from_string_literal(cls: Type['NFARegexBuilder'], literal: str) -> 'NFARegexBuilder':
        """
        Initialize this builder accepting only the given string literal
        """
        transitions: BuilderTransitionsT = {
            i: {chr: {i+1}}
            for i, chr in enumerate(literal)
        }

        final_state = len(literal)
        transitions[final_state] = dict()

        return cls(
            transitions = transitions,
            initial_state = 0,
            final_states = {final_state}
        )


    def union(self, other: 'NFARegexBuilder') -> None:
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


    def concatenate(self, other: 'NFARegexBuilder') -> None:
        """
        Apply the concatenate operation to the NFA represented by this builder
        and other.
        """
        self._transitions.update(other._transitions)

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).add(other._initial_state)

        self._final_states = other._final_states


    def kleene(self) -> None:
        """
        Apply the kleene star operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).update({self._initial_state})

        self._initial_state = new_initial_state
        self._final_states.add(new_initial_state)

    def option(self) -> None:
        """
        Apply the option operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        self._initial_state = new_initial_state
        self._final_states.add(new_initial_state)


    def copy(self) -> 'NFARegexBuilder':
        """
        Make a copy of this builder.
        """
        return NFARegexBuilder(
            transitions = self._transitions,
            initial_state = self._initial_state,
            final_states = self._final_states
        )


    @classmethod
    def __get_next_state_name(cls: Type['NFARegexBuilder']) -> int:
        return next(cls._state_name_counter)

class UnionToken(InfixOperator[NFARegexBuilder]):

    def get_precedence(self) -> int:
        return 1

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.union(right)
        return left

class KleeneToken(PostfixOperator[NFARegexBuilder]):

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.kleene()
        return left

class OptionToken(PostfixOperator[NFARegexBuilder]):

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.option()
        return left

class ConcatToken(InfixOperator[NFARegexBuilder]):

    def get_precedence(self) -> int:
        return 2

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.concatenate(right)
        return left

class StringToken(Literal[NFARegexBuilder]):

    def val(self) -> NFARegexBuilder:
        return NFARegexBuilder.from_string_literal(self.text)

SubsDictT = Dict[str, NFARegexBuilder]

def add_concat_tokens(token_list: List[Token[NFARegexBuilder]]) -> List[Token[NFARegexBuilder]]:
    "Add concat tokens to list of initially parsed tokens"
    final_token_list = []
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


def parse_regex(regexstr: str):
    if len(regexstr) == 0:
        return NFARegexBuilder.from_string_literal(regexstr)


    lexer: Lexer[NFARegexBuilder] = Lexer()

    lexer.register_token(lambda x: LeftParen(x), r'\(')
    lexer.register_token(lambda x: RightParen(x), r'\)')
    lexer.register_token(lambda x: StringToken(x), r'[A-Za-z0-9]')
    lexer.register_token(lambda x: UnionToken(x), r'\|')
    lexer.register_token(lambda x: ConcatToken(x), r'\.')
    lexer.register_token(lambda x: KleeneToken(x), r'\*')
    lexer.register_token(lambda x: OptionToken(x), r'\?')

    lexed_tokens = lexer.lex(regexstr)
    validate_tokens(lexed_tokens)
    tokens_with_concats = add_concat_tokens(lexed_tokens)
    postfix: List[Token[NFARegexBuilder]] = tokens_to_postfix(tokens_with_concats)

    return parse_postfix_tokens(postfix)
