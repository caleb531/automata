"""Classes and methods for parsing regexes into NFAs."""

from __future__ import annotations

import copy
import re
from collections import deque
from itertools import chain, count, product, repeat
from typing import AbstractSet, Deque, Dict, Iterable, List, Optional, Set, Tuple, Type

from typing_extensions import NoReturn, Self

import automata.base.exceptions as exceptions
from automata.base.utils import get_renaming_function, pairwise
from automata.regex.lexer import Lexer, Token
from automata.regex.postfix import (
    InfixOperator,
    LeftParen,
    Literal,
    PostfixOperator,
    RightParen,
    parse_postfix_tokens,
    tokens_to_postfix,
    validate_tokens,
)

BuilderTransitionsT = Dict[int, Dict[str, Set[int]]]

RESERVED_CHARACTERS = frozenset(
    ("*", "|", "(", ")", "?", " ", "\t", "&", "+", ".", "^", "{", "}", "[", "]")
)


class NFARegexBuilder:
    """Builder class designed for speed in parsing regular expressions into NFAs."""

    __slots__: Tuple[str, ...] = (
        "_transitions",
        "_initial_state",
        "_final_states",
        "_state_name_counter",
    )

    _transitions: BuilderTransitionsT
    _initial_state: int
    _final_states: Set[int]
    _state_name_counter: count

    def __init__(
        self,
        *,
        transitions: BuilderTransitionsT,
        initial_state: int,
        final_states: Set[int],
        counter: count,
    ) -> None:
        """
        Initialize new builder class
        """

        self._transitions = transitions
        self._initial_state = initial_state
        self._final_states = final_states
        self._state_name_counter = counter

    @classmethod
    def from_string_literal(
        cls: Type[NFARegexBuilder], literal: str, counter: count
    ) -> NFARegexBuilder:
        """
        Initialize this builder accepting only the given string literal
        """

        transitions: BuilderTransitionsT = {
            next(counter): {symbol: set()} for symbol in literal
        }

        for start_state, path in transitions.items():
            for end_states in path.values():
                end_states.add(start_state + 1)

        final_state = next(counter)
        transitions[final_state] = {}

        return cls(
            transitions=transitions,
            initial_state=min(transitions.keys()),
            final_states={final_state},
            counter=counter,
        )

    @classmethod
    def wildcard(
        cls: Type[NFARegexBuilder], input_symbols: AbstractSet[str], counter: count
    ) -> NFARegexBuilder:
        """
        Initialize this builder for a wildcard with the given input symbols
        """

        initial_state = next(counter)
        final_state = next(counter)

        transitions: BuilderTransitionsT = {
            initial_state: {symbol: {final_state} for symbol in input_symbols},
            final_state: {},
        }

        return cls(
            transitions=transitions,
            initial_state=initial_state,
            final_states={final_state},
            counter=counter,
        )

    def union(self, other: NFARegexBuilder) -> None:
        """
        Apply the union operation to the NFA represented by this builder and other
        """
        self._transitions.update(other._transitions)

        new_initial_state = next(self._state_name_counter)

        # Add epsilon transitions from new start state to old ones
        self._transitions[new_initial_state] = {
            "": {self._initial_state, other._initial_state}
        }

        self._initial_state = new_initial_state
        self._final_states.update(other._final_states)

    def intersection(self, other: NFARegexBuilder) -> None:
        """
        Apply the intersection operation to the NFA represented by this builder
        and other. Use BFS to only traverse reachable part (keeps number of
        states down).
        """

        get_state_name = get_renaming_function(self._state_name_counter)

        new_final_states = set()
        new_transitions: BuilderTransitionsT = {}
        new_initial_state = (self._initial_state, other._initial_state)

        new_initial_state_name = get_state_name(new_initial_state)
        new_input_symbols = tuple(
            set(
                chain.from_iterable(
                    transition_dict.keys()
                    for transition_dict in chain(
                        self._transitions.values(), other._transitions.values()
                    )
                )
            )
            - {""}
        )

        queue: Deque[Tuple[int, int]] = deque()

        queue.append(new_initial_state)
        new_transitions[new_initial_state_name] = {}

        while queue:
            curr_state = queue.popleft()
            curr_state_name = get_state_name(curr_state)
            q_a, q_b = curr_state

            if q_a in self._final_states and q_b in other._final_states:
                new_final_states.add(curr_state_name)

            # States we will consider adding to the queue
            next_states_iterables: List[Iterable[Tuple[int, int]]] = []

            # Get transition dict for states in self
            transitions_a = self._transitions.get(q_a, {})
            # Add epsilon transitions for first set of transitions
            epsilon_transitions_a = transitions_a.get("")
            if epsilon_transitions_a is not None:
                state_dict = new_transitions.setdefault(curr_state_name, {})
                state_dict.setdefault("", set()).update(
                    map(get_state_name, zip(epsilon_transitions_a, repeat(q_b)))
                )
                next_states_iterables.append(zip(epsilon_transitions_a, repeat(q_b)))

            # Get transition dict for states in other
            transitions_b = other._transitions.get(q_b, {})
            # Add epsilon transitions for second set of transitions
            epsilon_transitions_b = transitions_b.get("")
            if epsilon_transitions_b is not None:
                state_dict = new_transitions.setdefault(curr_state_name, {})
                state_dict.setdefault("", set()).update(
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

    def concatenate(self, other: NFARegexBuilder) -> None:
        """
        Apply the concatenate operation to the NFA represented by this builder
        and other.
        """
        self._transitions.update(other._transitions)

        for state in self._final_states:
            self._transitions[state].setdefault("", set()).add(other._initial_state)

        self._final_states = other._final_states

    def repeat(self, lower_bound: int, upper_bound: Optional[int]) -> None:
        """
        Apply the repetition operator. Corresponds to repeating the NFA
        between lower_bound and upper_bound many times. If upper_bound is None,
        then the number of repetitions is unbounded.
        """
        number_of_repetitions = lower_bound if upper_bound is None else upper_bound

        prev_final_states = self._final_states

        new_initial_state = next(self._state_name_counter)
        new_transitions = copy.deepcopy(self._transitions)

        new_transitions[new_initial_state] = {"": {self._initial_state}}

        new_final_states = set()

        if lower_bound <= 1:
            new_final_states.update(self._final_states)

        # Loop around if lower bound is 0
        if lower_bound == 0:
            new_final_states.add(self._initial_state)

        prev_initial_state = self._initial_state

        for i in range(2, number_of_repetitions + 1):
            # Reset the state renaming function each time
            get_state_name = get_renaming_function(self._state_name_counter)

            # Load next copy of transitions into dict
            new_transitions.update(
                {
                    get_state_name(start_state): {
                        char: set(map(get_state_name, dest_states))
                        for char, dest_states in char_transitions.items()
                    }
                    for start_state, char_transitions in self._transitions.items()
                }
            )

            for state in prev_final_states:
                new_transitions[state].setdefault("", set()).add(
                    get_state_name(self._initial_state)
                )

            prev_final_states = set(map(get_state_name, self._final_states))
            prev_initial_state = get_state_name(self._initial_state)

            # Wonky numbering because we start with one copy of states
            if lower_bound <= i:
                new_final_states.update(prev_final_states)

        # If no upper bound, make quantifier loop around
        if upper_bound is None:
            for state in prev_final_states:
                new_transitions[state].setdefault("", set()).add(prev_initial_state)

        self._transitions = new_transitions
        self._final_states = new_final_states
        self._initial_state = new_initial_state

    def shuffle_product(self, other: NFARegexBuilder) -> None:
        """
        Apply the shuffle operation to the NFA represented by this builder and other.
        No need for BFS since all states are accessible.
        """

        get_state_name = get_renaming_function(self._state_name_counter)

        self._initial_state = get_state_name(
            (self._initial_state, other._initial_state)
        )

        new_transitions: BuilderTransitionsT = {}

        transition_product = product(
            self._transitions.items(), other._transitions.items()
        )
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

        self._final_states = set(
            map(get_state_name, product(self._final_states, other._final_states))
        )
        self._transitions = new_transitions


class UnionToken(InfixOperator[NFARegexBuilder]):
    """Subclass of infix operator defining the union operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 1

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.union(right)
        return left


class IntersectionToken(InfixOperator[NFARegexBuilder]):
    """Subclass of infix operator defining the intersection operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 1

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.intersection(right)
        return left


class ShuffleToken(InfixOperator[NFARegexBuilder]):
    """Subclass of infix operator defining the shuffle operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 1

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.shuffle_product(right)
        return left


class KleeneStarToken(PostfixOperator[NFARegexBuilder]):
    """Subclass of postfix operator defining the kleene star operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.repeat(0, None)
        return left


class KleenePlusToken(PostfixOperator[NFARegexBuilder]):
    """Subclass of postfix operator defining the kleene plus operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.repeat(1, None)
        return left


class QuantifierToken(PostfixOperator[NFARegexBuilder]):
    """Subclass of postfix operator for repeating an expression a fixed number
    of times."""

    __slots__: Tuple[str, ...] = ("lower_bound", "upper_bound")

    def __init__(self, text: str, lower_bound: int, upper_bound: Optional[int]) -> None:
        super().__init__(text)

        if lower_bound < 0:
            raise exceptions.InvalidRegexError(
                f"Quantifier lower bound must be strictly greater than 0, not "
                f"{lower_bound}."
            )
        elif upper_bound is not None and upper_bound < lower_bound:
            raise exceptions.InvalidRegexError(
                f"Quantifier upper bound {upper_bound} inconsistent with lower "
                f"bound {lower_bound}."
            )

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @classmethod
    def from_match(cls: Type[Self], match: re.Match) -> Self:
        lower_bound_str = match.group(1)
        upper_bound_str = match.group(2)

        # Parse lower bound
        if not lower_bound_str:
            lower_bound = 0
        else:
            try:
                lower_bound = int(lower_bound_str)
                if lower_bound < 0:
                    raise exceptions.InvalidRegexError(
                        f"Lower bound cannot be negative: {lower_bound}"
                    )
            except ValueError:
                # This shouldn't happen with our regex pattern, but just in case
                raise exceptions.InvalidRegexError(
                    f"Invalid lower bound: {lower_bound_str}"
                )

        # Parse upper bound
        if upper_bound_str is None:
            # Format {n}
            upper_bound = lower_bound
        elif not upper_bound_str:
            # Format {n,}
            upper_bound = None
        else:
            try:
                upper_bound = int(upper_bound_str)
                if upper_bound < 0:
                    raise exceptions.InvalidRegexError(
                        f"Upper bound cannot be negative: {upper_bound}"
                    )
            except ValueError:
                # This shouldn't happen with our regex pattern, but just in case
                raise exceptions.InvalidRegexError(
                    f"Invalid upper bound: {upper_bound_str}"
                )

        # Validate bounds relationship
        if upper_bound is not None and lower_bound > upper_bound:
            raise exceptions.InvalidRegexError(
                f"Lower bound {lower_bound} cannot be "
                "greater than upper bound {upper_bound}"
            )

        return cls(match.group(), lower_bound, upper_bound)

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.repeat(self.lower_bound, self.upper_bound)
        return left


class OptionToken(PostfixOperator[NFARegexBuilder]):
    """Subclass of postfix operator defining the option operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 3

    def op(self, left: NFARegexBuilder) -> NFARegexBuilder:
        left.repeat(0, 1)
        return left


class ConcatToken(InfixOperator[NFARegexBuilder]):
    """Subclass of infix operator defining the concatenation operator."""

    __slots__: Tuple[str, ...] = tuple()

    def get_precedence(self) -> int:
        return 2

    def op(self, left: NFARegexBuilder, right: NFARegexBuilder) -> NFARegexBuilder:
        left.concatenate(right)
        return left


class StringToken(Literal[NFARegexBuilder]):
    """Subclass of literal token defining a string literal."""

    __slots__: Tuple[str, ...] = ("counter",)

    def __init__(self, text: str, counter: count) -> None:
        super().__init__(text)
        self.counter = counter

    @classmethod
    def from_match(cls: Type[Self], match: re.Match) -> NoReturn:
        raise NotImplementedError

    def val(self) -> NFARegexBuilder:
        return NFARegexBuilder.from_string_literal(self.text, self.counter)


class WildcardToken(Literal[NFARegexBuilder]):
    """Subclass of literal token defining a wildcard literal."""

    __slots__: Tuple[str, ...] = ("input_symbols", "counter")

    def __init__(
        self, text: str, input_symbols: AbstractSet[str], counter: count
    ) -> None:
        super().__init__(text)
        self.input_symbols = input_symbols
        self.counter = counter

    @classmethod
    def from_match(cls: Type[Self], match: re.Match) -> NoReturn:
        raise NotImplementedError

    def val(self) -> NFARegexBuilder:
        return NFARegexBuilder.wildcard(self.input_symbols, self.counter)


class CharacterClassToken(Literal[NFARegexBuilder]):
    """Subclass of literal token defining a character class."""

    __slots__: Tuple[str, ...] = ("input_symbols", "class_chars", "negated", "counter")

    def __init__(
        self,
        text: str,
        class_chars: Set[str],
        negated: bool,
        input_symbols: AbstractSet[str],
        counter: count,
    ) -> None:
        super().__init__(text)
        self.class_chars = class_chars
        self.negated = negated
        self.input_symbols = input_symbols
        self.counter = counter

    @classmethod
    def from_match(cls: Type[Self], match: re.Match) -> Self:
        content = match.group(1)

        # Process character ranges and build full content
        pos = 0
        expanded_content = ""
        while pos < len(content):
            if pos + 2 < len(content) and content[pos + 1] == "-":
                start_char, end_char = content[pos], content[pos + 2]
                if ord(start_char) <= ord(end_char):
                    # Include all characters in the range
                    expanded_content += "".join(
                        chr(i) for i in range(ord(start_char), ord(end_char) + 1)
                    )
                    pos += 3
                else:
                    # Invalid range - just add characters as is
                    expanded_content += content[pos]
                    pos += 1
            else:
                expanded_content += content[pos]
                pos += 1

        is_negated = content.startswith("^")
        if is_negated:
            expanded_content = expanded_content[1:]  # Remove ^ from the content

        return cls(match.group(), expanded_content, is_negated)

    def val(self) -> NFARegexBuilder:
        if self.negated:
            # For negated class, create an NFA accepting any character
            # not in class_chars
            acceptable_chars = self.input_symbols - self.class_chars
            return NFARegexBuilder.wildcard(acceptable_chars, self.counter)
        else:
            # Create an NFA accepting any character in the set
            return NFARegexBuilder.wildcard(self.class_chars, self.counter)


def add_concat_and_empty_string_tokens(
    token_list: List[Token[NFARegexBuilder]],
    state_name_counter: count,
) -> List[Token[NFARegexBuilder]]:
    """Add concat tokens to list of parsed infix tokens."""

    final_token_list = []
    # Pairs of token types to insert concat tokens in between
    concat_pairs = [
        (Literal, Literal),
        (RightParen, LeftParen),
        (RightParen, Literal),
        (Literal, LeftParen),
        (PostfixOperator, Literal),
        (PostfixOperator, LeftParen),
    ]

    # Pairs of tokens to insert empty string literals between
    empty_string_pairs = [(LeftParen, RightParen)]

    for curr_token, next_token in pairwise(token_list, True):
        final_token_list.append(curr_token)

        if next_token is not None:
            for firstClass, secondClass in concat_pairs:
                if isinstance(curr_token, firstClass) and isinstance(
                    next_token, secondClass
                ):
                    final_token_list.append(ConcatToken(""))
            for firstClass, secondClass in empty_string_pairs:
                if isinstance(curr_token, firstClass) and isinstance(
                    next_token, secondClass
                ):
                    final_token_list.append(StringToken("", state_name_counter))

    return final_token_list


def get_regex_lexer(
    input_symbols: AbstractSet[str], state_name_counter: count
) -> Lexer[NFARegexBuilder]:
    """Get lexer for parsing regular expressions."""
    lexer: Lexer[NFARegexBuilder] = Lexer()

    lexer.register_token(LeftParen.from_match, r"\(")
    lexer.register_token(RightParen.from_match, r"\)")
    lexer.register_token(UnionToken.from_match, r"\|")
    lexer.register_token(IntersectionToken.from_match, r"\&")
    lexer.register_token(ShuffleToken.from_match, r"\^")
    lexer.register_token(KleeneStarToken.from_match, r"\*")
    lexer.register_token(KleenePlusToken.from_match, r"\+")
    lexer.register_token(OptionToken.from_match, r"\?")
    # Match both {n}, {n,m}, and {,m} formats for quantifiers
    lexer.register_token(QuantifierToken.from_match, r"\{(-?\d*)(?:,(-?\d*))?\}")
    # Register wildcard and character classes next
    lexer.register_token(
        lambda match: WildcardToken(match.group(), input_symbols, state_name_counter),
        r"\.",
    )

    # Add character class token
    def character_class_factory(match: re.Match) -> CharacterClassToken:
        class_str = match.group()
        negated, class_chars = process_char_class(class_str)
        return CharacterClassToken(
            class_str, class_chars, negated, input_symbols, state_name_counter
        )

    lexer.register_token(
        character_class_factory,
        r"\[[^\]]*\]",  # Match anything between [ and ]
    )

    lexer.register_token(
        lambda match: StringToken(match.group(), state_name_counter), r"\S"
    )

    return lexer


def parse_regex(regexstr: str, input_symbols: AbstractSet[str]) -> NFARegexBuilder:
    """Return an NFARegexBuilder corresponding to regexstr."""

    if len(regexstr) == 0:
        return NFARegexBuilder.from_string_literal(regexstr, count(0))

    state_name_counter = count(0)

    lexer = get_regex_lexer(input_symbols, state_name_counter)
    lexed_tokens = lexer.lex(regexstr)
    validate_tokens(lexed_tokens)
    tokens_with_concats = add_concat_and_empty_string_tokens(
        lexed_tokens, state_name_counter
    )
    postfix = tokens_to_postfix(tokens_with_concats)

    return parse_postfix_tokens(postfix)


def process_char_class(class_str: str) -> Tuple[bool, Set[str]]:
    """Process a character class string into a set of characters and negation flag.

    Parameters
    ----------
    class_str : str
        The character class string including brackets, e.g., '[a-z]' or '[^abc]'

    Returns
    -------
    Tuple[bool, Set[str]]
        A tuple containing (is_negated, set_of_characters)
    """
    content = class_str[1:-1]

    if not content:
        raise exceptions.InvalidRegexError("Empty character class '[]' is not allowed")

    negated = content.startswith("^")
    if negated:
        content = content[1:]

        if not content:
            raise exceptions.InvalidRegexError(
                "Empty negated character class '[^]' is not allowed"
            )

    chars = set()
    i = 0
    while i < len(content):
        # Special case: - at the beginning or end is treated as literal
        if content[i] == "-" and (i == 0 or i == len(content) - 1):
            chars.add("-")
            i += 1
        # Handle ranges - but only when there are characters on both sides
        elif i + 2 < len(content) and content[i + 1] == "-":
            # Range like a-z
            start, end = content[i], content[i + 2]
            chars.update(chr(c) for c in range(ord(start), ord(end) + 1))
            i += 3
        else:
            chars.add(content[i])
            i += 1

    return negated, chars
