#!/usr/bin/env python3
"""Classes for working with all automata, including Turing machines."""

import abc
from typing import AbstractSet, Any, Dict, Generator, Mapping, NoReturn, Tuple

from frozendict import frozendict
from typing_extensions import Self

import automata.base.config as global_config
import automata.base.exceptions as exceptions
from automata.base.utils import freeze_value

AutomatonStateT = Any
AutomatonPathT = Mapping[str, Any]
AutomatonTransitionsT = Mapping[str, AutomatonPathT]


class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all automata, including Turing machines."""

    __slots__: Tuple[str, ...] = tuple()

    initial_state: AutomatonStateT
    states: AbstractSet[AutomatonStateT]
    final_states: AbstractSet[AutomatonStateT]
    transitions: AutomatonTransitionsT
    input_symbols: AbstractSet[str]

    def __init__(self, **kwargs: Any) -> None:
        if not global_config.allow_mutable_automata:
            for attr_name, attr_value in kwargs.items():
                object.__setattr__(self, attr_name, freeze_value(attr_value))
        else:
            for attr_name, attr_value in kwargs.items():
                object.__setattr__(self, attr_name, attr_value)
        self.__post_init__()

    def __post_init__(self) -> None:
        if global_config.should_validate_automata:
            self.validate()

    @abc.abstractmethod
    def validate(self) -> None:
        """Return True if this automaton is internally consistent."""
        raise NotImplementedError

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        """Set custom setattr to make class immutable."""
        raise AttributeError(f"This {type(self).__name__} is immutable")

    def __delattr__(self, name: str) -> None:
        """Set custom delattr to make class immutable."""
        raise AttributeError(f"This {type(self).__name__} is immutable")

    def __getstate__(self) -> Any:
        """Return the object's state, described by its input parameters"""
        return self.input_parameters

    def __setstate__(self, d: Dict[str, Any]) -> None:
        """Restore the object state from its input parameters"""
        # Notice that the default __setstate__ method won't work
        #   because __setattr__ is disabled due to immutability
        self.__init__(**d)  # type: ignore

    @abc.abstractmethod
    def read_input_stepwise(self, input_str: str) -> Generator[Any, None, None]:
        """Return a generator that yields each step while reading input."""
        raise NotImplementedError

    def read_input(self, input_str: str) -> AutomatonStateT:
        """
        Check if the given string is accepted by this automaton.

        Return the automaton's final configuration if this string is valid.
        """
        # "Fast-forward" generator to get its final value
        for config in self.read_input_stepwise(input_str):
            pass
        return config

    def accepts_input(self, input_str: str) -> bool:
        """Return True if this automaton accepts the given input."""
        try:
            self.read_input(input_str)
            return True
        except exceptions.RejectionException:
            return False

    def _validate_initial_state(self) -> None:
        """Raise an error if the initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                "{} is not a valid initial state".format(self.initial_state)
            )

    def _validate_initial_state_transitions(self) -> None:
        """Raise an error if the initial state has no transitions defined."""
        if self.initial_state not in self.transitions and len(self.states) > 1:
            raise exceptions.MissingStateError(
                "initial state {} has no transitions defined".format(self.initial_state)
            )

    def _validate_final_states(self) -> None:
        """Raise an error if any final states are invalid."""
        invalid_states = self.final_states - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                "final states are not valid ({})".format(
                    ", ".join(str(state) for state in invalid_states)
                )
            )

    @property
    def input_parameters(self) -> Dict[str, Any]:
        """Return the public attributes for this automaton."""
        return {
            attr_name: getattr(self, attr_name)
            for attr_name in self.__slots__
            if not attr_name.startswith("_")
        }

    def copy(self) -> Self:
        """Create a deep copy of the automaton."""
        return self.__class__(**self.input_parameters)

    # Format the given value for string output via repr() or str(); this exists
    # for the purpose of displaying

    def _get_repr_friendly_value(self, value: Any) -> Any:
        """
        A helper function to convert the given value / structure into a fully
        mutable one by recursively processing said structure and any of its
        members, unfreezing them along the way
        """
        if isinstance(value, frozenset):
            return set(value)
        elif isinstance(value, frozendict):
            return {
                dict_key: self._get_repr_friendly_value(dict_value)
                for dict_key, dict_value in value.items()
            }
        else:
            return value

    def __repr__(self) -> str:
        """Return a string representation of the automaton."""
        values = ", ".join(
            f"{attr_name}={self._get_repr_friendly_value(attr_value)!r}"
            for attr_name, attr_value in self.input_parameters.items()
        )
        return f"{self.__class__.__qualname__}({values})"

    def __contains__(self, item: Any) -> bool:
        """Returns whether the word is accepted by the automaton."""

        if not isinstance(item, str):
            return False

        return self.accepts_input(item)
