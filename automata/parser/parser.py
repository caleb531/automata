from __future__ import annotations
from itertools import zip_longest, count
from regular_expressions.lexer import Lexer, Token
from regular_expressions.postfix import InvalidTokenOrdering, LeftParen, RightParen, parse_postfix_tokens
from regular_expressions.postfix import InfixOperator, PostfixOperator, Literal, tokens_to_postfix, validate_tokens
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
import re

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
    def from_dfa(cls: Type[NFARegexBuilder], dfa: DFA) -> NFARegexBuilder:
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
    def from_string_literal(cls: Type[NFARegexBuilder], literal: str) -> NFARegexBuilder:
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


    def union(self, other: NFARegexBuilder) -> None:
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


    def concatenate(self, other: NFARegexBuilder) -> None:
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


    def copy(self) -> NFARegexBuilder:
        """
        Make a copy of this builder.
        """
        return NFARegexBuilder(
            transitions = self._transitions,
            initial_state = self._initial_state,
            final_states = self._final_states
        )


    def build(self, input_symbols: Set[str]) -> NFA:
        return NFA(
            states=set(self._transitions.keys()),
            input_symbols=input_symbols,
            transitions=self._transitions,
            initial_state=self._initial_state,
            final_states=self._final_states
        )


    @classmethod
    def __get_next_state_name(cls: Type[NFARegexBuilder]) -> int:
        return next(cls._state_name_counter)

class UnionToken(InfixOperator[NFARegexBuilder]):

    @classmethod
    def regexp(cls: Type[UnionToken]) -> str:
        return r'\+'

    def get_precedence(self) -> int:
        return 1

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.union(right)
        return left

class KleeneToken(PostfixOperator[NFARegexBuilder]):

    @classmethod
    def regexp(cls: Type[KleeneToken]) -> str:
        return r'\*'

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.kleene()
        return left

class ConcatToken(InfixOperator[NFARegexBuilder]):

    @classmethod
    def regexp(cls: Type[ConcatToken]) -> str:
        return r'\.'

    def get_precedence(self) -> int:
        return 2

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.concatenate(right)
        return left

class StringToken(Literal[NFARegexBuilder]):

    @classmethod
    def regexp(cls: Type[StringToken]) -> str:
        return r'[0-9]+'

    def val(self) -> NFARegexBuilder:
        return NFARegexBuilder.from_string_literal(self.text)

SubsDictT = Dict[str, NFARegexBuilder]

class VariableToken(Literal[NFARegexBuilder]):
    __slots__ = ['subs_dict']

    def __init__(self, text: str, subs_dict: SubsDictT) -> None:
        self.text = text
        self.subs_dict = subs_dict

    @classmethod
    def regexp(cls) -> str:
        return r'[A-Za-z]+'

    def val(self) -> NFARegexBuilder:
        if self.text not in self.subs_dict:
            raise InvalidTokenOrdering(f'Invalid variable name {self.text}')
        return self.subs_dict[self.text].copy()


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

def bind_kleene_star_to_literal(token_list: List[Token[NFARegexBuilder]]) -> List[Token[NFARegexBuilder]]:
    final_token_list: List[Token[NFARegexBuilder]] = []

    for curr_token, next_token in zip_longest(token_list, token_list[1:]):
        if isinstance(curr_token, StringToken) and isinstance(next_token, KleeneToken) and len(curr_token.text) > 1:
            text = curr_token.text[:-1]
            end = curr_token.text[-1]
            final_token_list.extend([StringToken(text), StringToken(end)])
        else:
            final_token_list.append(curr_token)

    return final_token_list


def compute_nfa_from_regex_lines(regex: str, alphabet: Set[str] = {'0', '1'}) -> NFA:
    "Computes an NFA from a multi-line regex statement"
    # Remove blank lines
    regex_lines = [line for line in regex.replace(' ', '').splitlines() if line]

    if not regex_lines:
        raise InvalidTokenOrdering("Cannot parse blank regular expression.")

    *all_but_last_line, last_line = regex_lines

    subs_dict: SubsDictT = {'e': NFARegexBuilder.from_string_literal('')}
    line_pattern = re.compile(r'\s*(\w+)\s*=\s*(.*)\s*')
    for regex_line in all_but_last_line:
        line_match = line_pattern.match(regex_line)

        if line_match is None:
            raise InvalidTokenOrdering(f"Invalid variable assignment in line '{regex_line}'")

        variable_name = line_match[1].strip()
        regex_statement = line_match[2]

        # For subexpression, minimize NFA for re-use later
        nfa = parse_regex_line(regex_statement, subs_dict).build(alphabet)
        subs_dict[variable_name] = NFARegexBuilder.from_dfa(DFA.from_nfa(nfa, retain_names=False).minify(retain_names=False))


    # TODO remove this and change test to catch different
    if '=' in last_line:
        raise InvalidTokenOrdering("The last line of your submission can't be used to define a subexpression")

    return parse_regex_line(last_line, subs_dict).build(alphabet)


def parse_regex_line(regexstr: str, subs_dict: SubsDictT) -> NFARegexBuilder:
    lexer: Lexer[NFARegexBuilder] = Lexer()

    lexer.register_token(lambda x: LeftParen(x), LeftParen.regexp())
    lexer.register_token(lambda x: RightParen(x), RightParen.regexp())
    lexer.register_token(lambda x: StringToken(x), StringToken.regexp())
    lexer.register_token(lambda x: UnionToken(x), UnionToken.regexp())
    lexer.register_token(lambda x: KleeneToken(x), KleeneToken.regexp())
    lexer.register_token(lambda x: ConcatToken(x), ConcatToken.regexp())

    lexer.register_token(lambda text: VariableToken(text, subs_dict), VariableToken.regexp())

    lexed_tokens = lexer.lex(regexstr)
    validate_tokens(lexed_tokens)
    kleene_bound_tokens = bind_kleene_star_to_literal(lexed_tokens)
    tokens_with_concats = add_concat_tokens(kleene_bound_tokens)
    postfix: List[Token[NFARegexBuilder]] = tokens_to_postfix(tokens_with_concats)

    return parse_postfix_tokens(postfix)
