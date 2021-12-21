#!/usr/bin/env python3
"""Classes and functions for testing the behavior of DFAs."""

import os
import os.path
import tempfile
import types
from unittest.mock import patch
from typing import Hashable, FrozenSet

import nose.tools as nose

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


def freeze(*items : Hashable) -> FrozenSet:
    return frozenset(items)

class TestDFA(test_fa.TestFA):
    """A test class for testing deterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_dfa(self) -> None:
        """Should copy DFA if passed into DFA constructor."""
        new_dfa = DFA.copy(self.dfa)
        self.assert_is_copy(new_dfa, self.dfa)

    def test_init_dfa_missing_formal_params(self):
        """Should raise an error if formal DFA parameters are missing."""
        with nose.assert_raises(TypeError):
            DFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_dfa(self) -> None:
        """Should create exact copy of DFA if copy() method is called."""
        new_dfa = self.dfa.copy()
        self.assert_is_copy(new_dfa, self.dfa)

    @patch('automata.fa.dfa.DFA.validate')
    def test_init_validation(self, validate) -> None:
        """Should validate DFA when initialized."""
        DFA.copy(self.dfa)
        validate.assert_called_once_with()

    def test_dfa_equal(self) -> None:
        """Should correctly determine if two DFAs are equal."""
        new_dfa = self.dfa.copy()
        nose.assert_true(self.dfa == new_dfa, 'DFAs are not equal')

    def test_dfa_not_equal(self) -> None:
        """Should correctly determine if two DFAs are not equal."""
        new_dfa = self.dfa.copy()
        new_dfa.final_states.add('q2')
        nose.assert_true(self.dfa != new_dfa, 'DFAs are equal')

    def test_validate_missing_state(self) -> None:
        """Should raise error if a state has no transitions defined."""
        with nose.assert_raises(exceptions.MissingStateError):
            del self.dfa.transitions['q1']
            self.dfa.validate()

    def test_validate_missing_symbol(self) -> None:
        """Should raise error if a symbol transition is missing."""
        with nose.assert_raises(exceptions.MissingSymbolError):
            del self.dfa.transitions['q1']['1']
            self.dfa.validate()

    def test_validate_invalid_symbol(self) -> None:
        """Should raise error if a transition references an invalid symbol."""
        with nose.assert_raises(exceptions.InvalidSymbolError):
            self.dfa.transitions['q1']['2'] = 'q2'
            self.dfa.validate()

    def test_validate_invalid_state(self) -> None:
        """Should raise error if a transition references an invalid state."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.transitions['q1']['1'] = 'q3'
            self.dfa.validate()

    def test_validate_invalid_initial_state(self) -> None:
        """Should raise error if the initial state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.initial_state = 'q3'
            self.dfa.validate()

    def test_validate_invalid_final_state(self) -> None:
        """Should raise error if the final state is invalid."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.final_states = {'q3'}
            self.dfa.validate()

    def test_validate_invalid_final_state_non_str(self) -> None:
        """Should raise InvalidStateError even for non-string final states."""
        with nose.assert_raises(exceptions.InvalidStateError):
            self.dfa.final_states = {3}
            self.dfa.validate()

    def test_read_input_accepted(self) -> None:
        """Should return correct state if acceptable DFA input is given."""
        nose.assert_equal(self.dfa.read_input('0111'), 'q1')

    def test_read_input_rejection(self) -> None:
        """Should raise error if the stop state is not a final state."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dfa.read_input('011')

    def test_read_input_rejection_invalid_symbol(self) -> None:
        """Should raise error if an invalid symbol is read."""
        with nose.assert_raises(exceptions.RejectionException):
            self.dfa.read_input('01112')

    def test_accepts_input_true(self) -> None:
        """Should return True if DFA input is accepted."""
        nose.assert_equal(self.dfa.accepts_input('0111'), True)

    def test_accepts_input_false(self) -> None:
        """Should return False if DFA input is rejected."""
        nose.assert_equal(self.dfa.accepts_input('011'), False)

    def test_read_input_step(self) -> None:
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.dfa.read_input_stepwise('0111')
        nose.assert_is_instance(validation_generator, types.GeneratorType)
        nose.assert_equal(list(validation_generator), [
            'q0', 'q0', 'q1', 'q2', 'q1'
        ])

    def test_operations_other_types(self):
        """Should raise NotImplementedError for all but equals."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        other = 42
        nose.assert_not_equal(dfa, other)
        with nose.assert_raises(NotImplementedError):
            dfa | other
        with nose.assert_raises(NotImplementedError):
            dfa & other
        with nose.assert_raises(NotImplementedError):
            dfa - other
        with nose.assert_raises(NotImplementedError):
            dfa ^ other
        with nose.assert_raises(NotImplementedError):
            dfa < other
        with nose.assert_raises(NotImplementedError):
            dfa <= other
        with nose.assert_raises(NotImplementedError):
            dfa > other
        with nose.assert_raises(NotImplementedError):
            dfa >= other

    def test_equivalence_not_equal(self) -> None:
        """Should not be equal."""
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        nose.assert_true(no_consecutive_11_dfa != zero_or_one_1_dfa)

    def test_equivalence_minify(self) -> None:
        """Should be equivalent after minify."""
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q3', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'},
                'q3': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q3'}
        )
        minimal_dfa = no_consecutive_11_dfa.minify()
        nose.assert_equal(no_consecutive_11_dfa, minimal_dfa)

    def test_equivalence_two_non_minimal(self) -> None:
        """Should be equivalent even though they are non minimal."""
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q3', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'},
                'q3': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q3'}
        )
        other_dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q2'},
                'q3': {'0': 'q3', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        nose.assert_equal(no_consecutive_11_dfa, other_dfa)

    def test_complement(self) -> None:
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        complement_dfa = ~no_consecutive_11_dfa
        nose.assert_equal(complement_dfa.states, no_consecutive_11_dfa.states)
        nose.assert_equal(
            complement_dfa.input_symbols, no_consecutive_11_dfa.input_symbols
        )
        nose.assert_equal(
            complement_dfa.transitions, no_consecutive_11_dfa.transitions
        )
        nose.assert_equal(
            complement_dfa.initial_state, no_consecutive_11_dfa.initial_state
        )
        nose.assert_equal(
            complement_dfa.final_states, {'q2'}
        )

    def test_union(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.union(B, retain_names=True, minify=False)
        nose.assert_equal(new_dfa.states, {
            freeze('q0','p0'), freeze('q0','p1'), freeze('q0','p2'),
            freeze('q1','p0'), freeze('q1','p1'), freeze('q1','p2'),
            freeze('q2','p0'), freeze('q2','p1'), freeze('q2','p2'),
            freeze('q3','p0'), freeze('q3','p1'), freeze('q3','p2'),
            freeze('q4','p0'), freeze('q4','p1'), freeze('q4','p2')
        })
        nose.assert_equal(new_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(new_dfa.transitions, {
            freeze('q0','p0'): {'0': freeze('q0','p0'), '1': freeze('q1','p1')},
            freeze('q0','p1'): {'0': freeze('q0','p0'), '1': freeze('q1','p2')},
            freeze('q0','p2'): {'0': freeze('q0','p2'), '1': freeze('q1','p2')},
            freeze('q1','p0'): {'0': freeze('q1','p0'), '1': freeze('q2','p1')},
            freeze('q1','p1'): {'0': freeze('q1','p0'), '1': freeze('q2','p2')},
            freeze('q1','p2'): {'0': freeze('q1','p2'), '1': freeze('q2','p2')},
            freeze('q2','p0'): {'0': freeze('q2','p0'), '1': freeze('q3','p1')},
            freeze('q2','p1'): {'0': freeze('q2','p0'), '1': freeze('q3','p2')},
            freeze('q2','p2'): {'0': freeze('q2','p2'), '1': freeze('q3','p2')},
            freeze('q3','p0'): {'0': freeze('q3','p0'), '1': freeze('q4','p1')},
            freeze('q3','p1'): {'0': freeze('q3','p0'), '1': freeze('q4','p2')},
            freeze('q3','p2'): {'0': freeze('q3','p2'), '1': freeze('q4','p2')},
            freeze('q4','p0'): {'0': freeze('q4','p0'), '1': freeze('q4','p1')},
            freeze('q4','p1'): {'0': freeze('q4','p0'), '1': freeze('q4','p2')},
            freeze('q4','p2'): {'0': freeze('q4','p2'), '1': freeze('q4','p2')}
        })
        nose.assert_equal(new_dfa.initial_state, freeze('q0','p0'))
        nose.assert_equal(new_dfa.final_states, {
            freeze('q0','p0'), freeze('q0','p1'),
            freeze('q1','p0'), freeze('q1','p1'),
            freeze('q2','p0'), freeze('q2','p1'),
            freeze('q3','p0'), freeze('q3','p1'),
            freeze('q4','p0'), freeze('q4','p1'), freeze('q4','p2')
        })

    def test_intersection(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.intersection(B, retain_names=True, minify=False)
        nose.assert_equal(new_dfa.states, {
            freeze('q0','p0'), freeze('q0','p1'), freeze('q0','p2'),
            freeze('q1','p0'), freeze('q1','p1'), freeze('q1','p2'),
            freeze('q2','p0'), freeze('q2','p1'), freeze('q2','p2'),
            freeze('q3','p0'), freeze('q3','p1'), freeze('q3','p2'),
            freeze('q4','p0'), freeze('q4','p1'), freeze('q4','p2')
        })
        nose.assert_equal(new_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(new_dfa.transitions, {
            freeze('q0','p0'): {'0': freeze('q0','p0'), '1': freeze('q1','p1')},
            freeze('q0','p1'): {'0': freeze('q0','p0'), '1': freeze('q1','p2')},
            freeze('q0','p2'): {'0': freeze('q0','p2'), '1': freeze('q1','p2')},
            freeze('q1','p0'): {'0': freeze('q1','p0'), '1': freeze('q2','p1')},
            freeze('q1','p1'): {'0': freeze('q1','p0'), '1': freeze('q2','p2')},
            freeze('q1','p2'): {'0': freeze('q1','p2'), '1': freeze('q2','p2')},
            freeze('q2','p0'): {'0': freeze('q2','p0'), '1': freeze('q3','p1')},
            freeze('q2','p1'): {'0': freeze('q2','p0'), '1': freeze('q3','p2')},
            freeze('q2','p2'): {'0': freeze('q2','p2'), '1': freeze('q3','p2')},
            freeze('q3','p0'): {'0': freeze('q3','p0'), '1': freeze('q4','p1')},
            freeze('q3','p1'): {'0': freeze('q3','p0'), '1': freeze('q4','p2')},
            freeze('q3','p2'): {'0': freeze('q3','p2'), '1': freeze('q4','p2')},
            freeze('q4','p0'): {'0': freeze('q4','p0'), '1': freeze('q4','p1')},
            freeze('q4','p1'): {'0': freeze('q4','p0'), '1': freeze('q4','p2')},
            freeze('q4','p2'): {'0': freeze('q4','p2'), '1': freeze('q4','p2')}
        })
        nose.assert_equal(new_dfa.initial_state, freeze('q0','p0'))
        nose.assert_equal(new_dfa.final_states, {
            freeze('q4','p0'), freeze('q4','p1'),
        })

    def frozenseterence(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.difference(B, retain_names=True, minify=False)
        nose.assert_equal(new_dfa.states, {
            freeze('q0','p0'), freeze('q0','p1'), freeze('q0','p2'),
            freeze('q1','p0'), freeze('q1','p1'), freeze('q1','p2'),
            freeze('q2','p0'), freeze('q2','p1'), freeze('q2','p2'),
            freeze('q3','p0'), freeze('q3','p1'), freeze('q3','p2'),
            freeze('q4','p0'), freeze('q4','p1'), freeze('q4','p2')
        })
        nose.assert_equal(new_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(new_dfa.transitions, {
            freeze('q0','p0') : {'0': freeze('q0','p0'), '1': freeze('q1','p1')},
            freeze('q0','p1'): {'0': freeze('q0','p0'), '1': freeze('q1','p2')},
            freeze('q0','p2'): {'0': freeze('q0','p2'), '1': freeze('q1','p2')},
            freeze('q1','p0'): {'0': freeze('q1','p0'), '1': freeze('q2','p1')},
            freeze('q1','p1'): {'0': freeze('q1','p0'), '1': freeze('q2','p2')},
            freeze('q1','p2'): {'0': freeze('q1','p2'), '1': freeze('q2','p2')},
            freeze('q2','p0'): {'0': freeze('q2','p0'), '1': freeze('q3','p1')},
            freeze('q2','p1'): {'0': freeze('q2','p0'), '1': freeze('q3','p2')},
            freeze('q2','p2'): {'0': freeze('q2','p2'), '1': freeze('q3','p2')},
            freeze('q3','p0'): {'0': freeze('q3','p0'), '1': freeze('q4','p1')},
            freeze('q3','p1'): {'0': freeze('q3','p0'), '1': freeze('q4','p2')},
            freeze('q3','p2'): {'0': freeze('q3','p2'), '1': freeze('q4','p2')},
            freeze('q4','p0'): {'0': freeze('q4','p0'), '1': freeze('q4','p1')},
            freeze('q4','p1'): {'0': freeze('q4','p0'), '1': freeze('q4','p2')},
            freeze('q4','p2'): {'0': freeze('q4','p2'), '1': freeze('q4','p2')}
        })
        nose.assert_equal(new_dfa.initial_state, freeze('q0','p0'))
        nose.assert_equal(new_dfa.final_states, {
            freeze('q4','p2')
        })

    def test_symmetric_difference(self) -> None:
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        new_dfa = A.symmetric_difference(B, retain_names=True, minify=False)
        nose.assert_equal(new_dfa.states, {
            freeze('q0','p0'), freeze('q0','p1'), freeze('q0','p2'),
            freeze('q1','p0'), freeze('q1','p1'), freeze('q1','p2'),
            freeze('q2','p0'), freeze('q2','p1'), freeze('q2','p2'),
            freeze('q3','p0'), freeze('q3','p1'), freeze('q3','p2'),
            freeze('q4','p0'), freeze('q4','p1'), freeze('q4','p2')
        })
        nose.assert_equal(new_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(new_dfa.transitions, {
            freeze('q0','p0'): {'0': freeze('q0','p0'), '1': freeze('q1','p1')},
            freeze('q0','p1'): {'0': freeze('q0','p0'), '1': freeze('q1','p2')},
            freeze('q0','p2'): {'0': freeze('q0','p2'), '1': freeze('q1','p2')},
            freeze('q1','p0'): {'0': freeze('q1','p0'), '1': freeze('q2','p1')},
            freeze('q1','p1'): {'0': freeze('q1','p0'), '1': freeze('q2','p2')},
            freeze('q1','p2'): {'0': freeze('q1','p2'), '1': freeze('q2','p2')},
            freeze('q2','p0'): {'0': freeze('q2','p0'), '1': freeze('q3','p1')},
            freeze('q2','p1'): {'0': freeze('q2','p0'), '1': freeze('q3','p2')},
            freeze('q2','p2'): {'0': freeze('q2','p2'), '1': freeze('q3','p2')},
            freeze('q3','p0'): {'0': freeze('q3','p0'), '1': freeze('q4','p1')},
            freeze('q3','p1'): {'0': freeze('q3','p0'), '1': freeze('q4','p2')},
            freeze('q3','p2'): {'0': freeze('q3','p2'), '1': freeze('q4','p2')},
            freeze('q4','p0'): {'0': freeze('q4','p0'), '1': freeze('q4','p1')},
            freeze('q4','p1'): {'0': freeze('q4','p0'), '1': freeze('q4','p2')},
            freeze('q4','p2'): {'0': freeze('q4','p2'), '1': freeze('q4','p2')}
        })
        nose.assert_equal(new_dfa.initial_state, freeze('q0','p0'))
        nose.assert_equal(new_dfa.final_states, {
            freeze('q0','p0'), freeze('q0','p1'),
            freeze('q1','p0'), freeze('q1','p1'),
            freeze('q2','p0'), freeze('q2','p1'),
            freeze('q3','p0'), freeze('q3','p1'),
            freeze('q4','p2')
        })

    def test_issubset(self) -> None:
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # Test both proper subset and subset with each set as left hand side
        nose.assert_true(zero_or_one_1_dfa < no_consecutive_11_dfa)
        nose.assert_true(zero_or_one_1_dfa <= no_consecutive_11_dfa)
        nose.assert_false(no_consecutive_11_dfa < zero_or_one_1_dfa)
        nose.assert_false(no_consecutive_11_dfa <= zero_or_one_1_dfa)

    def test_issuperset(self) -> None:
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        no_consecutive_11_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        zero_or_one_1_dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # Test both proper subset and subset with each set as left hand side
        nose.assert_false(zero_or_one_1_dfa > no_consecutive_11_dfa)
        nose.assert_false(zero_or_one_1_dfa >= no_consecutive_11_dfa)
        nose.assert_true(no_consecutive_11_dfa > zero_or_one_1_dfa)
        nose.assert_true(no_consecutive_11_dfa >= zero_or_one_1_dfa)

    def test_isdisjoint(self) -> None:
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q3'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        # This DFA accepts all words which contain either zero
        # or one occurrence of 1
        B = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        # This DFA accepts all words which contain at least
        # one occurrence of 1
        C = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q1'},
            },
            initial_state='q0',
            final_states={'q1'}
        )
        nose.assert_true(A.isdisjoint(B))
        nose.assert_true(B.isdisjoint(A))
        nose.assert_false(A.isdisjoint(C))
        nose.assert_false(B.isdisjoint(C))

    def test_isempty_non_empty(self) -> None:
        # This DFA accepts all words which contain at least
        # three occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q3'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_false(A.isempty())

    def test_isempty_empty(self) -> None:
        # This DFA has no reachable final states and
        # therefore accepts the empty language
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q0', '1': 'q1'},
                'q3': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_true(A.isempty())

    def test_isfinite_infinite(self) -> None:
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        nose.assert_false(A.isfinite())

    def test_isfinite_infinite_case_2(self) -> None:
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q2', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q3'},
                'q3': {'0': 'q4', '1': 'q4'},
                'q4': {'0': 'q5', '1': 'q5'},
                'q5': {'0': 'q6', '1': 'q6'},
                'q6': {'0': 'q6', '1': 'q6'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'}
        )
        nose.assert_false(A.isfinite())

    def test_isfinite_finite(self) -> None:
        # This DFA accepts all binary strings which have length
        # less than or equal to 5
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q2', '1': 'q2'},
                'q2': {'0': 'q3', '1': 'q3'},
                'q3': {'0': 'q4', '1': 'q4'},
                'q4': {'0': 'q5', '1': 'q5'},
                'q5': {'0': 'q6', '1': 'q6'},
                'q6': {'0': 'q6', '1': 'q6'}
            },
            initial_state='q0',
            final_states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}
        )
        nose.assert_true(A.isfinite())

    def test_isfinite_empty(self) -> None:
        # This DFA has no reachable final states and
        # therefore is finite.
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q0', '1': 'q1'},
                'q3': {'0': 'q2', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nose.assert_true(A.isfinite())

    def test_isfinite_universe(self) -> None:
        # This DFA accepts all binary strings and
        # therefore is infinite.
        A = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states={'q0'}
        )
        nose.assert_false(A.isfinite())

    def test_set_laws(self) -> None:
        """Tests many set laws that are true for all sets"""
        # This DFA accepts all words which contain at least four
        # occurrences of 1
        A = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q1', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q3'},
                'q3': {'0': 'q3', '1': 'q4'},
                'q4': {'0': 'q4', '1': 'q4'}
            },
            initial_state='q0',
            final_states={'q4'}
        )
        # This DFA accepts all words which do not contain two
        # consecutive occurrences of 1
        B = DFA(
            states={'p0', 'p1', 'p2'},
            input_symbols={'0', '1'},
            transitions={
                'p0': {'0': 'p0', '1': 'p1'},
                'p1': {'0': 'p0', '1': 'p2'},
                'p2': {'0': 'p2', '1': 'p2'}
            },
            initial_state='p0',
            final_states={'p0', 'p1'}
        )
        # This DFA accepts all binary strings
        U = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        # This DFA represents the empty language
        empty = DFA(
            states={'q0'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q0'}
            },
            initial_state='q0',
            final_states=set()
        )
        # De Morgan's laws
        nose.assert_equal(~(A | B), ~A & ~B)
        nose.assert_equal(~(A & B), ~A | ~B)
        # Complement laws
        nose.assert_equal(A | ~A, U)
        nose.assert_equal(A & ~A, empty)
        nose.assert_equal(~U, empty)
        nose.assert_equal(~empty, U)
        # Involution
        nose.assert_equal(A, ~(~A))
        # Relationships between relative and absolute complements
        nose.assert_equal(A - B, A & ~B)
        nose.assert_equal(~(A - B), ~A | B)
        nose.assert_equal(~(A - B), ~A | (B & A))
        # Relationship with set difference
        nose.assert_equal(~A - ~B, B - A)
        # Symmetric difference
        nose.assert_equal(A ^ B, (A - B) | (B - A))
        nose.assert_equal(A ^ B, (A | B) - (A & B))
        # Commutativity
        nose.assert_equal(A | B, B | A)
        nose.assert_equal(A & B, B & A)
        nose.assert_equal(A ^ B, B ^ A)

    def test_minify_dfa(self) -> None:
        """Should minify a given DFA."""
        # This DFA accepts all words which are at least two characters long.
        # The states q1/q2 and q3/q4/q5/q6 are redundant.
        # The state q7 is not reachable.
        dfa = DFA(
            states={'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q2'},
                'q1': {'0': 'q3', '1': 'q4'},
                'q2': {'0': 'q5', '1': 'q6'},
                'q3': {'0': 'q3', '1': 'q3'},
                'q4': {'0': 'q4', '1': 'q4'},
                'q5': {'0': 'q5', '1': 'q5'},
                'q6': {'0': 'q6', '1': 'q6'},
                'q7': {'0': 'q7', '1': 'q7'}
            },
            initial_state='q0',
            final_states={'q3', 'q4', 'q5', 'q6'}
        )
        minimal_dfa = dfa.minify(retain_names=True)
        nose.assert_equal(minimal_dfa.states, {
            'q0', freeze('q1','q2'), freeze('q3','q4','q5','q6')
        })
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            'q0': {'0': freeze('q1','q2'), '1': freeze('q1','q2')},
            freeze('q1','q2'): {'0': freeze('q3','q4','q5','q6'), '1': freeze('q3','q4','q5','q6')},
            freeze('q3','q4','q5','q6'): {'0': freeze('q3','q4','q5','q6'), '1': freeze('q3','q4','q5','q6')}
        })
        nose.assert_equal(minimal_dfa.initial_state, 'q0')
        nose.assert_equal(minimal_dfa.final_states, {freeze('q3','q4','q5','q6')})

    def test_minify_dfa_complex(self) -> None:
        """Should minify a given large DFA."""
        dfa = DFA(
            states={'13', '56', '18', '10', '15', '26', '24', '54', '32', '27',
                    '5', '43', '8', '3', '17', '45', '57', '46', '35', '9',
                    '0', '21', '39', '51', '6', '55', '47', '11', '20', '12',
                    '59', '38', '44', '52', '16', '41', '1', '4', '28', '58',
                    '48', '23', '22', '2', '31', '36', '34', '49', '40', '7',
                    '25', '30', '53', '42', '33', '19', '50', '37', '14',
                    '29'},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={'55': {'L': '20', 'U': '49', 'R': '20', 'D': '49'},
                         '57': {'L': '5', 'U': '6', 'R': '1', 'D': '46'},
                         '35': {'L': '44', 'U': '32', 'R': '36', 'D': '33'},
                         '13': {'L': '45', 'U': '23', 'R': '45', 'D': '23'},
                         '43': {'L': '44', 'U': '32', 'R': '44', 'D': '33'},
                         '9': {'L': '5', 'U': '6', 'R': '1', 'D': '6'},
                         '53': {'L': '20', 'U': '33', 'R': '20', 'D': '32'},
                         '12': {'L': '40', 'U': '23', 'R': '25', 'D': '11'},
                         '42': {'L': '1', 'U': '49', 'R': '5', 'D': '49'},
                         '24': {'L': '40', 'U': '48', 'R': '25', 'D': '23'},
                         '27': {'L': '5', 'U': '46', 'R': '1', 'D': '6'},
                         '22': {'L': '40', 'U': '48', 'R': '25', 'D': '11'},
                         '19': {'L': '36', 'U': '32', 'R': '44', 'D': '33'},
                         '59': {'L': '40', 'U': '48', 'R': '45', 'D': '11'},
                         '39': {'L': '45', 'U': '48', 'R': '25', 'D': '11'},
                         '51': {'L': '20', 'U': '18', 'R': '20', 'D': '18'},
                         '34': {'L': '5', 'U': '4', 'R': '1', 'D': '31'},
                         '33': {'L': '44', 'U': '0', 'R': '36', 'D': '28'},
                         '23': {'L': '45', 'U': '8', 'R': '45', 'D': '8'},
                         '46': {'L': '44', 'U': '0', 'R': '44', 'D': '28'},
                         '58': {'L': '5', 'U': '4', 'R': '1', 'D': '4'},
                         '50': {'L': '20', 'U': '28', 'R': '20', 'D': '0'},
                         '54': {'L': '40', 'U': '8', 'R': '25', 'D': '41'},
                         '49': {'L': '1', 'U': '18', 'R': '5', 'D': '18'},
                         '21': {'L': '40', 'U': '26', 'R': '25', 'D': '8'},
                         '16': {'L': '5', 'U': '31', 'R': '1', 'D': '4'},
                         '6': {'L': '40', 'U': '26', 'R': '25', 'D': '41'},
                         '32': {'L': '36', 'U': '0', 'R': '44', 'D': '28'},
                         '48': {'L': '40', 'U': '26', 'R': '45', 'D': '41'},
                         '11': {'L': '45', 'U': '26', 'R': '25', 'D': '41'},
                         '15': {'L': '14', 'U': '49', 'R': '14', 'D': '49'},
                         '1': {'L': '56', 'U': '6', 'R': '37', 'D': '46'},
                         '3': {'L': '4', 'U': '32', 'R': '17', 'D': '33'},
                         '45': {'L': '8', 'U': '23', 'R': '8', 'D': '23'},
                         '52': {'L': '4', 'U': '32', 'R': '4', 'D': '33'},
                         '36': {'L': '56', 'U': '6', 'R': '37', 'D': '6'},
                         '20': {'L': '14', 'U': '33', 'R': '14', 'D': '32'},
                         '25': {'L': '47', 'U': '23', 'R': '10', 'D': '11'},
                         '29': {'L': '37', 'U': '49', 'R': '56', 'D': '49'},
                         '40': {'L': '47', 'U': '48', 'R': '10', 'D': '23'},
                         '5': {'L': '56', 'U': '46', 'R': '37', 'D': '6'},
                         '44': {'L': '47', 'U': '48', 'R': '10', 'D': '11'},
                         '38': {'L': '17', 'U': '32', 'R': '4', 'D': '33'},
                         '2': {'L': '47', 'U': '48', 'R': '8', 'D': '11'},
                         '30': {'L': '8', 'U': '48', 'R': '10', 'D': '11'},
                         '7': {'L': '14', 'U': '18', 'R': '14', 'D': '18'},
                         '37': {'L': '56', 'U': '4', 'R': '37', 'D': '31'},
                         '28': {'L': '4', 'U': '0', 'R': '17', 'D': '28'},
                         '8': {'L': '8', 'U': '8', 'R': '8', 'D': '8'},
                         '31': {'L': '4', 'U': '0', 'R': '4', 'D': '28'},
                         '17': {'L': '56', 'U': '4', 'R': '37', 'D': '4'},
                         '14': {'L': '14', 'U': '28', 'R': '14', 'D': '0'},
                         '10': {'L': '47', 'U': '8', 'R': '10', 'D': '41'},
                         '18': {'L': '37', 'U': '18', 'R': '56', 'D': '18'},
                         '47': {'L': '47', 'U': '26', 'R': '10', 'D': '8'},
                         '56': {'L': '56', 'U': '31', 'R': '37', 'D': '4'},
                         '4': {'L': '47', 'U': '26', 'R': '10', 'D': '41'},
                         '0': {'L': '17', 'U': '0', 'R': '4', 'D': '28'},
                         '26': {'L': '47', 'U': '26', 'R': '8', 'D': '41'},
                         '41': {'L': '8', 'U': '26', 'R': '10', 'D': '41'}},
            initial_state='55',
            final_states={'15', '24', '54', '32', '27', '5', '43', '57', '3',
                          '46', '35', '9', '21', '39', '51', '6', '55', '11',
                          '20', '12', '59', '38', '44', '52', '16', '1', '58',
                          '48', '22', '2', '36', '34', '49', '40', '25', '30',
                          '53', '42', '33', '19', '50', '29'})
        check_dfa = DFA(
            states={'5', '36', '1', '49', '40', '25', '46', '6', '55',
                    '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}', '33',
                    '11', '20', '48', '44', '32'},
            input_symbols={'L', 'U', 'R', 'D'},
            transitions={
                '48':
                {'L': '40',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '44':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '48',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '11'},
                '40':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '48',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '33':
                {'L': '44',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '36',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '55': {'L': '20', 'U': '49', 'R': '20', 'D': '49'},
                '32':
                {'L': '36',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '44',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '46':
                {'L': '44',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '44',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '25':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '11'},
                '6':
                {'L': '40',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '25',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '11':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '25',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '5':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '46',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '6'},
                '49':
                {'L': '1',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '5',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}'},
                '20':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '33',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '32'},
                '36':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '6',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '6'},
                '1':
                {'L': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'U': '6',
                 'R': '{0,10,14,17,18,23,26,28,31,37,4,41,45,47,56,8}',
                 'D': '46'}},
            initial_state='55',
            final_states={'5', '1', '36', '49', '40', '25', '46', '6', '55',
                          '33', '11', '20', '48', '44', '32'})
        minimal_dfa = dfa.minify(retain_names=True)
        nose.assert_equal(minimal_dfa.states, check_dfa.states)
        nose.assert_equal(minimal_dfa.input_symbols, check_dfa.input_symbols)
        nose.assert_equal(minimal_dfa.transitions, check_dfa.transitions)
        nose.assert_equal(minimal_dfa.initial_state, check_dfa.initial_state)
        nose.assert_equal(minimal_dfa.final_states, check_dfa.final_states)

    def test_minify_minimal_dfa(self) -> None:
        """Should minify an already minimal DFA."""
        # This DFA just accepts words ending in 1.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q1'}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        minimal_dfa = dfa.minify(retain_names=True)
        nose.assert_equal(minimal_dfa.states, dfa.states)
        nose.assert_equal(minimal_dfa.input_symbols, dfa.input_symbols)
        nose.assert_equal(minimal_dfa.transitions, dfa.transitions)
        nose.assert_equal(minimal_dfa.initial_state, dfa.initial_state)
        nose.assert_equal(minimal_dfa.final_states, dfa.final_states)

    def test_minify_dfa_initial_state(self) -> None:
        """Should minify a DFA where the initial state is being changed."""
        # This DFA accepts all words with ones and zeroes.
        # The two states can be merged into one.
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states={'q0', 'q1'},
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {freeze('q0','q1')})
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            freeze('q0','q1'): {'0': freeze('q0','q1'), '1': freeze('q0','q1')},
        })
        nose.assert_equal(minimal_dfa.initial_state, freeze('q0','q1'))
        nose.assert_equal(minimal_dfa.final_states, {freeze('q0','q1')})

    def test_minify_dfa_no_final_states(self) -> None:
        dfa = DFA(
            states={'q0', 'q1'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q1', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q0'},
            },
            initial_state='q0',
            final_states=set(),
        )
        minimal_dfa = dfa.minify()
        nose.assert_equal(minimal_dfa.states, {freeze('q0','q1')})
        nose.assert_equal(minimal_dfa.input_symbols, {'0', '1'})
        nose.assert_equal(minimal_dfa.transitions, {
            freeze('q0','q1'): {'0': freeze('q0','q1'), '1': freeze('q0','q1')},
        })
        nose.assert_equal(minimal_dfa.initial_state, freeze('q0','q1'))
        nose.assert_equal(minimal_dfa.final_states, set())

    def test_init_nfa_simple(self) -> None:
        """Should convert to a DFA a simple NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}},
                'q1': {'1': {'q2'}},
                'q2': {}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA.from_nfa(nfa)
        nose.assert_equal(dfa.states, {freeze(), freeze('q0'), freeze('q0','q1'), freeze('q2')})
        nose.assert_equal(dfa.input_symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            freeze(): {'0': freeze(), '1': freeze()},
            freeze('q0'): {'0': freeze('q0','q1'), '1': freeze()},
            freeze('q0','q1'): {'0': freeze('q0','q1'), '1': freeze('q2')},
            freeze('q2'): {'0': freeze(), '1': freeze()}
        })
        nose.assert_equal(dfa.initial_state, freeze('q0'))
        nose.assert_equal(dfa.final_states, {freeze('q2')})

    def test_init_nfa_more_complex(self) -> None:
        """Should convert to a DFA a more complex NFA."""
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0', 'q1'}, '1': {'q0'}},
                'q1': {'0': {'q1'}, '1': {'q2'}},
                'q2': {'0': {'q2'}, '1': {'q1'}}
            },
            initial_state='q0',
            final_states={'q2'}
        )
        dfa = DFA.from_nfa(nfa)
        nose.assert_equal(dfa.states, {
            freeze('q0'), freeze('q0','q1'), freeze('q0','q2'), freeze('q0','q1','q2')
        })
        nose.assert_equal(dfa.input_symbols, {'0', '1'})
        nose.assert_equal(dfa.transitions, {
            freeze('q0'): {'1': freeze('q0'), '0': freeze('q0','q1')},
            freeze('q0','q1'): {'1': freeze('q0','q2'), '0': freeze('q0','q1')},
            freeze('q0','q2'): {'1': freeze('q0','q1'), '0': freeze('q0','q1','q2')},
            freeze('q0','q1','q2'): {'1': freeze('q0','q1','q2'), '0': freeze('q0','q1','q2')}
        })
        nose.assert_equal(dfa.initial_state, freeze('q0'))
        nose.assert_equal(dfa.final_states, {freeze('q0','q1','q2'), freeze('q0','q2')})

    def test_init_nfa_lambda_transition(self) -> None:
        """Should convert to a DFA an NFA with a lambda transition."""
        dfa = DFA.from_nfa(self.nfa)
        nose.assert_equal(dfa.states, {freeze(), freeze('q0'), freeze('q1','q2')})
        nose.assert_equal(dfa.input_symbols, {'a', 'b'})
        nose.assert_equal(dfa.transitions, {
            freeze() : {'a': freeze(), 'b': freeze()},
            freeze('q0') : {'a': freeze('q1', 'q2'), 'b': freeze()},
            freeze('q1', 'q2') : {'a': freeze('q1', 'q2'), 'b': freeze('q0')},
        })
        nose.assert_equal(dfa.initial_state, freeze('q0'))
        nose.assert_equal(dfa.final_states, {freeze('q1', 'q2')})

    def test_nfa_to_dfa_with_lambda_transitions(self):
        """ Test NFA->DFA when initial state has lambda transitions """
        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'': {'q2'}},
                'q1': {'a': {'q1'}},
                'q2': {'a': {'q1'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        dfa = DFA.from_nfa(nfa)  # returns an equivalent DFA
        nose.assert_equal(dfa.read_input('a'), freeze('q1'))

    def test_partial_dfa(self) -> None:
        """Should allow for partial DFA when flag is set"""
        dfa = DFA(
            states={'', 'a', 'b', 'aa', 'bb', 'ab', 'ba'},
            input_symbols={'a', 'b'},
            transitions={
                '': {'a': 'a', 'b': 'b'},
                'a': {'b': 'ab', 'a': 'aa'},
                'b': {'b': 'bb'},
                'aa': {'a': 'aa', 'b': 'ab'},
                'bb': {'a': 'ba'},
                'ab': {'b': 'bb'},
                'ba': {'a': 'aa'}
            },
            initial_state='',
            final_states={'aa'},
            allow_partial=True
        )
        nose.assert_equal(dfa.read_input('aa'), 'aa')

    def test_show_diagram_initial_final_different(self) -> None:
        """
        Should construct the diagram for a DFA whose initial state
        is not a final state.
        """
        graph = self.dfa.show_diagram()
        nose.assert_equal(
            {node.get_name() for node in graph.get_nodes()},
            {'q0', 'q1', 'q2'})
        nose.assert_equal(graph.get_node('q0')[0].get_style(), 'filled')
        nose.assert_equal(graph.get_node('q1')[0].get_peripheries(), 2)
        nose.assert_equal(graph.get_node('q2')[0].get_peripheries(), None)
        nose.assert_equal(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', '0', 'q0'),
                ('q0', '1', 'q1'),
                ('q1', '0', 'q0'),
                ('q1', '1', 'q2'),
                ('q2', '0', 'q2'),
                ('q2', '1', 'q1')
            })

    def test_show_diagram_initial_final_same(self) -> None:
        """
        Should construct the diagram for a DFA whose initial state
        is also a final state.
        """
        # This DFA accepts all words which do not contain two consecutive
        # occurrences of 1
        dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        graph = dfa.show_diagram()
        nose.assert_equal(
            {node.get_name() for node in graph.get_nodes()},
            {'q0', 'q1', 'q2'})
        nose.assert_equal(graph.get_node('q0')[0].get_style(), 'filled')
        nose.assert_equal(graph.get_node('q0')[0].get_peripheries(), 2)
        nose.assert_equal(graph.get_node('q1')[0].get_peripheries(), 2)
        nose.assert_equal(graph.get_node('q2')[0].get_peripheries(), None)
        nose.assert_equal(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', '0', 'q0'),
                ('q0', '1', 'q1'),
                ('q1', '0', 'q0'),
                ('q1', '1', 'q2'),
                ('q2', '0', 'q2'),
                ('q2', '1', 'q2')
            })

    def test_show_diagram_write_file(self) -> None:
        """
        Should construct the diagram for a DFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, 'test_dfa.png')
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        nose.assert_false(os.path.exists(diagram_path))
        self.dfa.show_diagram(path=diagram_path)
        nose.assert_true(os.path.exists(diagram_path))
        os.remove(diagram_path)
