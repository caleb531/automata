#!/usr/bin/env python3
"""Classes and methods for parsing regexes into NFAs."""

from collections import deque
from itertools import chain, count, pairwise, product, repeat

from automata.base.utils import get_renaming_function
from automata.regex.lexer import Lexer
from automata.regex.postfix import (InfixOperator, LeftParen, Literal,
                                    PostfixOperator, RightParen,
                                    parse_postfix_tokens, tokens_to_postfix,
                                    validate_tokens)

RESERVED_CHARACTERS = frozenset({'*', '|', '(', ')', '?', ' ', '\t', '&', '+', '.', '^'})


class NFARegexBuilder:
    """Builder class designed for speed in parsing regular expressions into NFAs."""

    __slots__ = ('_transitions', '_initial_state', '_final_states')
    _state_name_counter = count(0)

    def __init__(self, *, transitions, initial_state, final_states):
        """
        Initialize new builder class
        """

        self._transitions = transitions
        self._initial_state = initial_state
        self._final_states = final_states

    @classmethod
    def from_string_literal(cls, literal):
        """
        Initialize this builder accepting only the given string literal
        """

        transitions = {
            cls.__get_next_state_name(): {chr: set()}
            for chr in literal
        }

        for start_state, path in transitions.items():
            for end_states in path.values():
                end_states.add(start_state+1)

        final_state = cls.__get_next_state_name()
        transitions[final_state] = {}

        return cls(
            transitions=transitions,
            initial_state=min(transitions.keys()),
            final_states={final_state}
        )

    @classmethod
    def wildcard(cls, input_symbols):
        """
        Initialize this builder for a wildcard with the given input symbols
        """

        initial_state = cls.__get_next_state_name()
        final_state = cls.__get_next_state_name()

        transitions = {
            initial_state: {symbol: {final_state} for symbol in input_symbols},
            final_state: {}
        }

        return cls(
            transitions=transitions,
            initial_state=initial_state,
            final_states={final_state}
        )

    def union(self, other):
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

    def intersection(self, other):
        """
        Apply the intersection operation to the NFA represented by this builder and other.
        Use BFS to only traverse reachable part (keeps number of states down).
        """

        get_state_name = get_renaming_function(self._state_name_counter)

        new_final_states = set()
        new_transitions = {}
        new_initial_state = (self._initial_state, other._initial_state)

        new_initial_state_name = get_state_name(new_initial_state)
        new_input_symbols = tuple(set(chain.from_iterable(
            map(dict.keys, chain(self._transitions.values(), other._transitions.values()))
        )) - {''})

        queue = deque()

        queue.append(new_initial_state)
        new_transitions[new_initial_state_name] = {}

        while queue:
            curr_state = queue.popleft()
            curr_state_name = get_state_name(curr_state)
            q_a, q_b = curr_state

            if q_a in self._final_states and q_b in other._final_states:
                new_final_states.add(curr_state_name)

            # States we will consider adding to the queue
            next_states_iterables = list()

            # Get transition dict for states in self
            transitions_a = self._transitions.get(q_a, {})
            # Add epsilon transitions for first set of transitions
            epsilon_transitions_a = transitions_a.get('')
            if epsilon_transitions_a is not None:
                state_dict = new_transitions.setdefault(curr_state_name, {})
                state_dict.setdefault('', set()).update(
                    map(get_state_name, zip(epsilon_transitions_a, repeat(q_b)))
                )
                next_states_iterables.append(zip(epsilon_transitions_a, repeat(q_b)))

            # Get transition dict for states in other
            transitions_b = other._transitions.get(q_b, {})
            # Add epsilon transitions for second set of transitions
            epsilon_transitions_b = transitions_b.get('')
            if epsilon_transitions_b is not None:
                state_dict = new_transitions.setdefault(curr_state_name, {})
                state_dict.setdefault('', set()).update(
                    map(get_state_name, zip(repeat(q_a), epsilon_transitions_b))
                )
                next_states_iterables.append(zip(repeat(q_a), epsilon_transitions_b))

            # Add all transitions moving over same input symbols
            for symbol in new_input_symbols:
                end_states_a = transitions_a.get(symbol)
                end_states_b = transitions_b.get(symbol)

                if end_states_a is not None and end_states_b is not None:
                    state_dict = new_transitions.setdefault(curr_state_name, {})
                    state_dict.setdefault(symbol, set()).update(
                        map(get_state_name, product(end_states_a, end_states_b))
                    )
                    next_states_iterables.append(product(end_states_a, end_states_b))

            # Finally, try visiting every state we found.
            for product_state in chain.from_iterable(next_states_iterables):
                product_state_name = get_state_name(product_state)
                if product_state_name not in new_transitions:
                    new_transitions[product_state_name] = {}
                    queue.append(product_state)

        self._final_states = new_final_states
        self._transitions = new_transitions
        self._initial_state = new_initial_state_name

    def concatenate(self, other):
        """
        Apply the concatenate operation to the NFA represented by this builder
        and other.
        """
        self._transitions.update(other._transitions)

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).add(other._initial_state)

        self._final_states = other._final_states

    def kleene_star(self):
        """
        Apply the kleene star operation to the NFA represented by this builder
        """
        self.kleene_plus()
        self._final_states.add(self._initial_state)

    def kleene_plus(self):
        """
        Apply the kleene plus operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        for state in self._final_states:
            self._transitions[state].setdefault('', set()).add(self._initial_state)

        self._initial_state = new_initial_state

    def option(self):
        """
        Apply the option operation to the NFA represented by this builder
        """
        new_initial_state = self.__get_next_state_name()

        self._transitions[new_initial_state] = {
            '': {self._initial_state}
        }

        self._initial_state = new_initial_state
        self._final_states.add(new_initial_state)

    def shuffle_product(self, other):
        """
        Apply the shuffle operation to the NFA represented by this builder and other.
        No need for BFS since all states are accessible.
        """

        get_state_name = get_renaming_function(self._state_name_counter)

        self._initial_state = get_state_name((self._initial_state, other._initial_state))

        new_transitions = {}

        transition_product = product(self._transitions.items(), other._transitions.items())
        for (q_a, transitions_a), (q_b, transitions_b) in transition_product:
            state_dict = new_transitions.setdefault(get_state_name((q_a, q_b)), {})

            for symbol, end_states in transitions_a.items():
                state_dict.setdefault(symbol, set()).update(
                    map(get_state_name, zip(end_states, repeat(q_b)))
                )

            for symbol, end_states in transitions_b.items():
                state_dict.setdefault(symbol, set()).update(
                    map(get_state_name, zip(repeat(q_a), end_states))
                )

        self._final_states = set(map(get_state_name, product(self._final_states, other._final_states)))
        self._transitions = new_transitions

    @classmethod
    def __get_next_state_name(cls):
        return next(cls._state_name_counter)


class UnionToken(InfixOperator):
    """Subclass of infix operator defining the union operator."""

    def get_precedence(self):
        return 1

    def op(self, left, right):
        left.union(right)
        return left


class IntersectionToken(InfixOperator):
    """Subclass of infix operator defining the intersection operator."""

    def get_precedence(self):
        return 1

    def op(self, left, right):
        left.intersection(right)
        return left


class ShuffleToken(InfixOperator):
    """Subclass of infix operator defining the shuffle operator."""

    def get_precedence(self):
        return 1

    def op(self, left, right):
        left.shuffle_product(right)
        return left


class KleeneStarToken(PostfixOperator):
    """Subclass of postfix operator defining the kleene star operator."""

    def get_precedence(self):
        return 3

    def op(self, left):
        left.kleene_star()
        return left


class KleenePlusToken(PostfixOperator):
    """Subclass of postfix operator defining the kleene plus operator."""

    def get_precedence(self):
        return 3

    def op(self, left):
        left.kleene_plus()
        return left


class OptionToken(PostfixOperator):
    """Subclass of postfix operator defining the option operator."""

    def get_precedence(self):
        return 3

    def op(self, left):
        left.option()
        return left


class ConcatToken(InfixOperator):
    """Subclass of infix operator defining the concatenation operator."""

    def get_precedence(self):
        return 2

    def op(self, left, right):
        left.concatenate(right)
        return left


class StringToken(Literal):
    """Subclass of literal token defining a string literal."""

    def val(self):
        return NFARegexBuilder.from_string_literal(self.text)


class WildcardToken(Literal):
    """Subclass of literal token defining a wildcard literal."""

    def __init__(self, text, input_symbols):
        super().__init__(text)
        self.input_symbols = input_symbols

    def val(self):
        return NFARegexBuilder.wildcard(self.input_symbols)


def add_concat_tokens(token_list):
    """Add concat tokens to list of parsed infix tokens."""

    final_token_list = []

    # Pairs of token types to insert concat tokens in between
    concat_pairs = [
        (Literal, Literal),
        (RightParen, LeftParen),
        (RightParen, Literal),
        (Literal, LeftParen),
        (PostfixOperator, Literal),
        (PostfixOperator, LeftParen)
    ]

    for curr_token, next_token in pairwise(chain(token_list, repeat(None, 1))):
        final_token_list.append(curr_token)

        if next_token is not None:
            for firstClass, secondClass in concat_pairs:
                if isinstance(curr_token, firstClass) and isinstance(next_token, secondClass):
                    final_token_list.append(ConcatToken(''))

    return final_token_list


def get_regex_lexer(input_symbols):
    """Get lexer for parsing regular expressions."""
    lexer = Lexer()

    lexer.register_token(LeftParen, r'\(')
    lexer.register_token(RightParen, r'\)')
    lexer.register_token(StringToken, r'[A-Za-z0-9]')
    lexer.register_token(UnionToken, r'\|')
    lexer.register_token(IntersectionToken, r'\&')
    lexer.register_token(ShuffleToken, r'\^')
    lexer.register_token(KleeneStarToken, r'\*')
    lexer.register_token(KleenePlusToken, r'\+')
    lexer.register_token(OptionToken, r'\?')
    lexer.register_token(lambda text: WildcardToken(text, input_symbols), r'\.')

    return lexer


def parse_regex(regexstr, input_symbols):
    """Return an NFARegexBuilder corresponding to regexstr."""

    if len(regexstr) == 0:
        return NFARegexBuilder.from_string_literal(regexstr)

    lexer = get_regex_lexer(input_symbols)
    lexed_tokens = lexer.lex(regexstr)
    validate_tokens(lexed_tokens)
    tokens_with_concats = add_concat_tokens(lexed_tokens)
    postfix = tokens_to_postfix(tokens_with_concats)

    return parse_postfix_tokens(postfix)
