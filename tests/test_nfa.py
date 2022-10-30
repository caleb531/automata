#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""
import os
import string
import tempfile
import types
from itertools import product
from unittest.mock import patch

from frozendict import frozendict

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_init_nfa_missing_formal_params(self):
        """Should raise an error if formal NFA parameters are missing."""
        with self.assertRaises(TypeError):
            NFA(
                states={'q0', 'q1'},
                input_symbols={'0', '1'},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_copy_nfa(self):
        """Should create exact copy of NFA if copy() method is called."""
        new_nfa = self.nfa.copy()
        self.assertIsNot(new_nfa, self.nfa)

    def test_nfa_immutable_attr_set(self):
        with self.assertRaises(AttributeError):
            self.nfa.states = {}

    def test_nfa_immutable_attr_del(self):
        with self.assertRaises(AttributeError):
            del self.nfa.states

    def test_nfa_immutable_dict(self):
        """Should create an NFA whose contents are fully immutable/hashable"""
        self.assertIsInstance(hash(frozendict(self.nfa.input_parameters)), int)

    def test_init_dfa(self):
        """Should convert DFA to NFA if passed into NFA constructor."""
        nfa = NFA.from_dfa(self.dfa)
        self.assertEqual(nfa.states, {'q0', 'q1', 'q2'})
        self.assertEqual(nfa.input_symbols, {'0', '1'})
        self.assertEqual(nfa.transitions, {
            'q0': {'0': {'q0'}, '1': {'q1'}},
            'q1': {'0': {'q0'}, '1': {'q2'}},
            'q2': {'0': {'q2'}, '1': {'q1'}}
        })
        self.assertEqual(nfa.initial_state, 'q0')

    @patch('automata.fa.nfa.NFA.validate')
    def test_init_validation(self, validate):
        """Should validate NFA when initialized."""
        self.nfa.copy()
        validate.assert_called_once_with()

    def test_nfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        nfa1 = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'': {'q1'}},
                'q1': {'a': {'q2'}},
                'q2': {'a': {'q2'}, '': {'q3'}},
                'q3': {'b': {'q1'}}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        nfa2 = NFA(
            states={0, 1, 2, 3},
            input_symbols={'a', 'b'},
            transitions={
                0: {'': {1}},
                1: {'a': {2}},
                2: {'a': {2}, '': {3}},
                3: {'b': {1}}
            },
            initial_state=0,
            final_states={3}
        )
        self.assertEqual(nfa1, nfa2)
        self.assertEqual(nfa1.eliminate_lambda(), nfa2.eliminate_lambda())

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        nfa1 = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}},
                'q1': {'a': {'q1'}, '': {'q2'}},
                'q2': {'b': {'q0'}}
            },
            initial_state='q0',
            final_states={'q1'}
        )
        nfa2 = NFA(
            states={'q0'},
            input_symbols={'a'},
            transitions={
                'q0': {'a': {'q0'}}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        self.assertNotEqual(nfa1, nfa2)

    def test_validate_invalid_symbol(self):
        """Should raise error if a transition references an invalid symbol."""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'b': {'q0'}}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_invalid_state(self):
        """Should raise error if a transition references an invalid state."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': {'q1'}}
                },
                initial_state='q0',
                final_states={'q0'}
            )

    def test_validate_invalid_initial_state(self):
        """Should raise error if the initial state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': {'q0'}}
                },
                initial_state='q1',
                final_states={'q0'}
            )

    def test_validate_initial_state_transitions(self):
        """Should raise error if the initial state has no transitions."""
        with self.assertRaises(exceptions.MissingStateError):
            NFA(
                states={'q0', 'q1'},
                input_symbols={'a'},
                transitions={},
                initial_state='q0',
                final_states={'q1'}
            )

    def test_validate_invalid_final_state(self):
        """Should raise error if the final state is invalid."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': {'q0'}}
                },
                initial_state='q0',
                final_states={'q1'}
            )

    def test_validate_invalid_final_state_non_str(self):
        """Should raise InvalidStateError even for non-string final states."""
        with self.assertRaises(exceptions.InvalidStateError):
            NFA(
                states={'q0'},
                input_symbols={'a'},
                transitions={
                    'q0': {'a': {'q0'}}
                },
                initial_state='q0',
                final_states={3}
            )
            self.nfa.validate()

    def test_read_input_accepted(self):
        """Should return correct states if acceptable NFA input is given."""
        self.assertEqual(self.nfa.read_input('aba'), {'q1', 'q2'})

    def test_validate_missing_state(self):
        """Should silently ignore states without transitions defined."""
        NFA(
            states={'q0'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q0'}}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        self.assertIsNotNone(self.nfa.transitions)

    def test_read_input_rejection(self):
        """Should raise error if the stop state is not a final state."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input('abba')

    def test_read_input_rejection_invalid_symbol(self):
        """Should raise error if an invalid symbol is read."""
        with self.assertRaises(exceptions.RejectionException):
            self.nfa.read_input('abc')

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise('aba')
        self.assertIsInstance(validation_generator, types.GeneratorType)
        self.assertEqual(list(validation_generator), [
            {'q0'}, {'q1', 'q2'}, {'q0'}, {'q1', 'q2'}
        ])

    def test_accepts_input_true(self):
        """Should return True if NFA input is accepted."""
        self.assertTrue(self.nfa.accepts_input('aba'))

    def test_accepts_input_false(self):
        """Should return False if NFA input is rejected."""
        self.assertFalse(self.nfa.accepts_input('abba'))

    def test_cyclic_lambda_transitions(self):
        """Should traverse NFA containing cyclic lambda transitions."""
        # NFA which matches zero or more occurrences of 'a'
        nfa = NFA(
            states={'q0', 'q1', 'q2', 'q3'},
            input_symbols={'a'},
            transitions={
                'q0': {'': {'q1', 'q3'}},
                'q1': {'a': {'q2'}},
                'q2': {'': {'q3'}},
                'q3': {'': {'q0'}}
            },
            initial_state='q0',
            final_states={'q3'}
        )
        self.assertEqual(nfa.read_input(''), {'q0', 'q1', 'q3'})
        self.assertEqual(nfa.read_input('a'), {'q0', 'q1', 'q2', 'q3'})

    def test_non_str_states(self):
        """Should handle non-string state names"""
        nfa = NFA(
            states={0},
            input_symbols={0},
            transitions={0: {}},
            initial_state=0,
            final_states=set())
        # We don't care what the output is, just as long as no exception is
        # raised
        self.assertIsNotNone(nfa.accepts_input(''))

    def test_operations_other_type(self):
        """Should raise TypeError for concatenate."""
        nfa = NFA(
            states={'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={'q1': {'0': {'q1'}, '1': {'q1', 'q2'}},
                         'q2': {'': {'q2'}, '0': {'q2'}},
                         'q3': {'1': {'q4'}},
                         'q4': {'0': {'q4'}, '1': {'q4'}}},
            initial_state='q1',
            final_states={'q2', 'q4'})
        other = 42
        with self.assertRaises(TypeError):
            nfa + other

    def test_concatenate(self):
        nfa_a = NFA(
            states={'q1', 'q2', 'q3', 'q4'},
            input_symbols={'0', '1'},
            transitions={
                'q1': {'0': {'q1'}, '1': {'q1', 'q2'}},
                'q2': {'': {'q2'}, '0': {'q2'}},
                'q3': {'1': {'q4'}},
                'q4': {'0': {'q4'}, '1': {'q4'}}
            },
            initial_state='q1',
            final_states={'q2', 'q4'}
        )

        nfa_b = NFA(
            states={'r1', 'r2', 'r3'},
            input_symbols={'0', '1'},
            transitions={
                'r1': {'': {'r3'}, '1': {'r2'}},
                'r2': {'0': {'r2', 'r3'}, '1': {'r3'}},
                'r3': {'0': {'r1'}}
            },
            initial_state='r1',
            final_states={'r1'}
        )

        concat_nfa = nfa_a + nfa_b

        self.assertFalse(concat_nfa.accepts_input(''))
        self.assertFalse(concat_nfa.accepts_input('0'))
        self.assertTrue(concat_nfa.accepts_input('1'))
        self.assertFalse(concat_nfa.accepts_input('00'))
        self.assertTrue(concat_nfa.accepts_input('01'))
        self.assertTrue(concat_nfa.accepts_input('10'))
        self.assertTrue(concat_nfa.accepts_input('11'))
        self.assertTrue(concat_nfa.accepts_input('101'))
        self.assertTrue(concat_nfa.accepts_input('101100'))
        self.assertTrue(concat_nfa.accepts_input('1010'))

    def test_kleene_star(self):
        """Should perform the Kleene Star operation on an NFA"""
        # This NFA accepts aa and ab
        nfa = NFA(
            states={0, 1, 2, 3, 4, 6, 10},
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1, 3}},
                1: {'b': {2}},
                2: {},
                3: {'a': {4}},
                4: {'': {6}},
                6: {}
            },
            initial_state=0,
            final_states={2, 4, 6, 10}
        )
        # This NFA should then accept any number of repetitions
        # of aa or ab concatenated together.
        kleene_nfa = nfa.kleene_star()
        self.assertTrue(kleene_nfa.accepts_input(''))
        self.assertFalse(kleene_nfa.accepts_input('a'))
        self.assertFalse(kleene_nfa.accepts_input('b'))
        self.assertTrue(kleene_nfa.accepts_input('aa'))
        self.assertTrue(kleene_nfa.accepts_input('ab'))
        self.assertFalse(kleene_nfa.accepts_input('ba'))
        self.assertFalse(kleene_nfa.accepts_input('bb'))
        self.assertFalse(kleene_nfa.accepts_input('aaa'))
        self.assertFalse(kleene_nfa.accepts_input('aba'))
        self.assertTrue(kleene_nfa.accepts_input('abaa'))
        self.assertFalse(kleene_nfa.accepts_input('abba'))
        self.assertFalse(kleene_nfa.accepts_input('aaabababaaaaa'))
        self.assertTrue(kleene_nfa.accepts_input('aaabababaaaaab'))
        self.assertFalse(kleene_nfa.accepts_input('aaabababaaaaba'))

    def test_reverse(self):
        """Should reverse an NFA"""
        nfa = NFA(
            states={0, 1, 2, 4},
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1}},
                1: {'a': {2}, 'b': {1, 2}},
                2: {},
                3: {'a': {2}, 'b': {2}}
            },
            initial_state=0,
            final_states={2}
        )
        reverse_nfa = reversed(nfa)
        self.assertFalse(reverse_nfa.accepts_input('a'))
        self.assertFalse(reverse_nfa.accepts_input('ab'))
        self.assertTrue(reverse_nfa.accepts_input('ba'))
        self.assertTrue(reverse_nfa.accepts_input('bba'))
        self.assertTrue(reverse_nfa.accepts_input('bbba'))

    def test_from_regex(self):
        """Test if from_regex produces correct NFA"""
        nfa1 = NFA.from_regex('ab(cd*|dc)|a?')
        nfa2 = NFA(
            states={0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
            input_symbols={'a', 'b', 'c', 'd'},
            initial_state=0,
            transitions={
                0: {'': {1, 10}},
                1: {'a': {2}},
                2: {'b': {3}},
                3: {'': {4, 7}},
                4: {'d': {5}},
                5: {'c': {6}},
                7: {'c': {8}},
                8: {'d': {9}},
                9: {'d': {9}},
                10: {'a': {11}}
            },
            final_states={6, 8, 9, 10, 11}
        )

        self.assertEqual(nfa1, nfa2)

    def test_from_regex_empty_string(self):
        NFA.from_regex('')

    def test_eliminate_lambda(self):
        original_nfa = NFA(
            states={0, 1, 2, 3, 4, 5, 6},
            initial_state=0,
            input_symbols={'a', 'b', 'c'},
            transitions={
                0: {'a': {1}},
                1: {'': {2, 6}, 'b': {2}},
                2: {'': {4}, 'c': {3}},
                4: {'a': {5}}
            },
            final_states={3, 6}
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)
        nfa2 = NFA(
            states={0, 1, 2, 3, 5},
            initial_state=0,
            input_symbols={'a', 'b', 'c'},
            transitions={
                0: {'a': {1}},
                1: {'a': {5}, 'b': {2}, 'c': {3}},
                2: {'a': {5}, 'c': {3}}
            },
            final_states={1, 3}
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(nfa1._lambda_closures, original_nfa._lambda_closures)

    def test_eliminate_lambda_other(self):
        original_nfa = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1}},
                1: {'': {2}, 'b': {1}},
                2: {'b': {2}}
            },
            final_states={2}
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)

        nfa2 = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={'a', 'b'},
            transitions={
                0: {'a': {1}},
                1: {'b': {1, 2}},
                2: {'b': {2}}
            },
            final_states={1, 2}
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(nfa1._lambda_closures, original_nfa._lambda_closures)

    def test_eliminate_lambda_regex(self):
        nfa = NFA.from_regex('a(aaa*bbcd|abbcd)d*|aa*bb(dcc*|(d|c)b|a?bb(dcc*|(d|c)))ab(c|d)*(ccd)?')
        nfa_without_lambdas = nfa.eliminate_lambda()
        self.assertEqual(nfa, nfa_without_lambdas)

        for transition in nfa_without_lambdas.transitions.values():
            for char in transition.keys():
                self.assertNotEqual(char, '')

    def test_option(self):
        """
        Given a NFA recognizing language L, should return NFA
        such that it accepts the language 'L?'
        that zero or one occurrence of L.
        """
        nfa1 = NFA.from_regex('a*b')
        nfa1 = nfa1.option()
        self.assertTrue(nfa1.accepts_input('aab'))
        self.assertTrue(nfa1.initial_state in nfa1.final_states
                        and nfa1.initial_state
                        not in sum([list(nfa1.transitions[state].values()) for state in nfa1.transitions.keys()], []))

    def test_union(self):
        nfa1 = NFA.from_regex('ab*')
        nfa2 = NFA.from_regex('ba*')

        nfa3 = nfa1.union(nfa2)

        nfa4 = NFA(
            states={0, 1, 2, 3, 4},
            input_symbols={'a', 'b'},
            transitions={
                0: {'': {1, 3}},
                2: {'b': {2}},
                1: {'a': {2}},
                3: {'b': {4}},
                4: {'a': {4}}
            },
            final_states={2, 4},
            initial_state=0
        )

        self.assertEqual(nfa3, nfa4)

        # second check
        nfa5 = nfa1 | nfa2
        self.assertEqual(nfa5, nfa4)

        # third check: union of NFA which is subset of other
        nfa6 = NFA.from_regex('aa*')
        nfa7 = NFA.from_regex('a*')
        nfa8 = nfa6.union(nfa7)
        nfa9 = nfa7.union(nfa6)
        self.assertEqual(nfa8, nfa7)
        self.assertEqual(nfa9, nfa7)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa | self.dfa

    def test_intersection(self):
        nfa1 = NFA.from_regex('aaaa*')
        nfa2 = NFA.from_regex('(a)|(aa)|(aaa)')

        nfa3 = nfa1.intersection(nfa2)

        nfa4 = NFA.from_regex('aaa')
        self.assertEqual(nfa3, nfa4)
        # second check
        nfa5 = nfa1 & nfa2

        self.assertEqual(nfa5, nfa4)

        # third check: intersection of NFA which is subset of other
        nfa6 = NFA.from_regex('aa*')
        nfa7 = NFA.from_regex('a*')
        nfa8 = nfa6.intersection(nfa7)
        nfa9 = nfa7.intersection(nfa6)
        self.assertEqual(nfa8, nfa6)
        self.assertEqual(nfa9, nfa6)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa & self.dfa

    def test_validate_regex(self):
        """Should raise an error if invalid regex is passed into NFA.from_regex()"""

        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'ab|')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, '?')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'a|b|*')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'a||b')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, '((abc*)))((abd)')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, '*')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'abcd()')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'ab(bc)*((bbcd)')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'a(*)')
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, 'ab(|)')

    def test_from_symbol(self):
        """Should generate NFA from single transition symbol"""

        nfa1 = NFA._from_symbol('a')

        nfa2 = NFA(
            states={0, 1},
            input_symbols={'a'},
            initial_state=0,
            transitions={0: {'a': {1}}},
            final_states={1}
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)

    def test_from_symbol_input_symbols(self):
        """Should generate NFA from single transition symbol"""

        nfa1 = NFA._from_symbol('a', input_symbols={'a', 'b'})

        nfa2 = NFA(
            states={0, 1},
            input_symbols={'a', 'b'},
            initial_state=0,
            transitions={0: {'a': {1}}},
            final_states={1}
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)

    def test_show_diagram_initial_final_same(self):
        """
        Should construct the diagram for a NFA whose initial state
        is also a final state.
        """

        nfa = NFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'a', 'b'},
            transitions={
                'q0': {'a': {'q1'}},
                'q1': {'a': {'q1'}, '': {'q2'}},
                'q2': {'b': {'q0'}}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
        graph = nfa.show_diagram()
        self.assertEqual(
            {node.get_name() for node in graph.get_nodes()},
            {'q0', 'q1', 'q2'})
        self.assertEqual(graph.get_node('q0')[0].get_style(), 'filled')
        self.assertEqual(graph.get_node('q0')[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q1')[0].get_peripheries(), 2)
        self.assertEqual(graph.get_node('q2')[0].get_peripheries(), None)
        self.assertEqual(
            {(edge.get_source(), edge.get_label(), edge.get_destination())
             for edge in graph.get_edges()},
            {
                ('q0', 'a', 'q1'),
                ('q1', 'a', 'q1'),
                ('q1', '', 'q2'),
                ('q2', 'b', 'q0')
            })

    def test_show_diagram_write_file(self):
        """
        Should construct the diagram for a NFA
        and write it to the specified file.
        """
        diagram_path = os.path.join(self.temp_dir_path, 'test_dfa.png')
        try:
            os.remove(diagram_path)
        except OSError:
            pass
        self.assertFalse(os.path.exists(diagram_path))
        self.nfa.show_diagram(path=diagram_path)
        self.assertTrue(os.path.exists(diagram_path))
        os.remove(diagram_path)

    def test_add_new_state_type_integrity(self):
        """
        Should properly add new state of different type than original states;
        see <https://github.com/caleb531/automata/issues/60> for more details
        """
        A = NFA(
            states={'0', '1'},
            input_symbols={'0'},
            transitions={'0': {'0': {'1'}}, '1': {'0': {'1'}}},
            initial_state='0',
            final_states={'1'}
        )

        B = DFA.from_nfa(A.reverse())

        self.assertEqual(
            A.accepts_input('00'),
            B.accepts_input('00'),
            'DFA and NFA are not equivalent when they should be')

    def test_nfa_equality(self):
        nfa1 = NFA(
            states={'s', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'},
            input_symbols={'0', '1'},
            transitions={
                's': {'0': {'g'}, '1': {'a'}},
                'a': {'0': {'b'}, '': {'d'}},
                'b': {'1': {'c'}},
                'c': {'0': {'a'}},
                'd': {'1': {'e'}, '': {'f'}},
                'e': {'1': {'d'}},
                'f': {'':  {'s'}},
                'g': {'1': {'h'}},
                'h': {'0': {'f'}},
            },
            initial_state='s',
            final_states={'s'}
        )

        self.assertEqual(nfa1, NFA.from_regex('((1(010)*(11)*)|(010))*'))

        nfa2 = NFA(
            states={'s', 'a', 'b', 'c', 'd', 'e'},
            input_symbols={'0', '1'},
            transitions={
                's': {'0': {'a'}, '1': {'s'}, '': {'b', 'd'}},
                'a': {'1': {'s'}},
                'b': {'0': {'b'}, '1': {'c'}},
                'c': {'0': {'c'}, '1': {'e'}},
                'd': {'0': {'c'}, '1': {'d'}},
                'e': {'0': {'c'}},
            },
            initial_state='s',
            final_states={'c'}
        )

        self.assertEqual(nfa2, NFA.from_regex('(((01) | 1)*)((0*1) | (1*0))(((10) | 0)*)'))

        nfa3 = NFA(
            states={'s', '0', '1', '00', '01', '10', '11'},
            input_symbols={'0', '1'},
            transitions={
                's':  {'0': {'0'},  '1': {'1'}},
                '0':  {'0': {'00'}, '1': {'01'}},
                '1':  {'0': {'10'}, '1': {'11'}},
                '00': {'0': {'00'}, '1': {'01'}},
                '01': {'0': {'00'}, '1': {'01'}},
                '10': {'0': {'10'}, '1': {'11'}},
                '11': {'0': {'10'}, '1': {'11'}},
            },
            initial_state='s',
            final_states={'00', '11'}
        )

        self.assertEqual(nfa3, NFA.from_regex('(0(0 | 1)*0) | (1(0 | 1)*1)'))

        nfa4 = NFA(
            states={'s', '0', '1', '00', '01', '10', '11'},
            input_symbols={'0', '1'},
            transitions={
                's':  {'0': {'0'},  '1': {'1'}},
                '0':  {'0': {'00'}, '1': {'01'}},
                '1':  {'0': {'10'}, '1': {'11'}},
                '00': {'0': {'00'}, '1': {'01'}},
                '01': {'0': {'10'}, '1': {'11'}},
                '10': {'0': {'00'}, '1': {'01'}},
                '11': {'0': {'10'}, '1': {'11'}},
            },
            initial_state='s',
            final_states={'00', '11'}
        )

        self.assertEqual(nfa4, NFA.from_regex('((0 | 1)*00) | ((0 | 1)*11)'))

        nfa5 = NFA(
            states={'s', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'},
            input_symbols={'0', '1', '2'},
            transitions={
                's': {'': {'a', 'f', 'g'}, '2': {'c'}},
                'a': {'0': {'b', 'c'}},
                'b': {'1': {'a'}},
                'c': {'1': {'s', 'd'}},
                'd': {'0': {'e'}},
                'e': {'0': {'c'}},
                'f': {'1': {'f'}},
                'g': {'0': {'g'}, '': {'h'}},
                'h': {'2': {'h'}}
            },
            initial_state='s',
            final_states={'f', 'h'}
        )

        self.assertEqual(nfa5, NFA.from_regex('((((01)*0) | 2)(100)*1)*(1* | (0*2*))'))

    def test_nfa_levenshtein_distance(self):
        alphabet = {'f', 'o', 'd', 'a'}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {'f': {(1, 0), (1, 1), (0, 1)}, 'a': {(0, 1), (1, 1)},
                         'o': {(0, 1), (1, 1)}, 'd': {(0, 1), (1, 1)}, '': {(1, 1)}},
                (0, 1): {'f': {(1, 1), (1, 2), (0, 2)}, 'a': {(0, 2), (1, 2)},
                         'o': {(0, 2), (1, 2)}, 'd': {(0, 2), (1, 2)}, '': {(1, 2)}},
                (0, 2): {'f': {(1, 2)}},
                (1, 0): {'o': {(1, 1), (2, 0), (2, 1)}, 'a': {(1, 1), (2, 1)},
                         'f': {(1, 1), (2, 1)}, 'd': {(1, 1), (2, 1)}, '': {(2, 1)}},
                (1, 1): {'o': {(1, 2), (2, 1), (2, 2)}, 'a': {(1, 2), (2, 2)},
                         'f': {(1, 2), (2, 2)}, 'd': {(1, 2), (2, 2)}, '': {(2, 2)}},
                (1, 2): {'o': {(2, 2)}},
                (2, 0): {'o': {(3, 1), (2, 1), (3, 0)}, 'a': {(3, 1), (2, 1)},
                         'f': {(3, 1), (2, 1)}, 'd': {(3, 1), (2, 1)}, '': {(3, 1)}},
                (2, 1): {'o': {(3, 1), (3, 2), (2, 2)}, 'a': {(3, 2), (2, 2)},
                         'f': {(3, 2), (2, 2)}, 'd': {(3, 2), (2, 2)}, '': {(3, 2)}},
                (2, 2): {'o': {(3, 2)}},
                (3, 0): {'d': {(3, 1), (4, 0), (4, 1)}, 'a': {(3, 1), (4, 1)},
                         'f': {(3, 1), (4, 1)}, 'o': {(3, 1), (4, 1)}, '': {(4, 1)}},
                (3, 1): {'d': {(3, 2), (4, 1), (4, 2)}, 'a': {(3, 2), (4, 2)},
                         'f': {(3, 2), (4, 2)}, 'o': {(3, 2), (4, 2)}, '': {(4, 2)}},
                (3, 2): {'d': {(4, 2)}},
                (4, 0): {'a': {(4, 1)}, 'f': {(4, 1)}, 'o': {(4, 1)}, 'd': {(4, 1)}},
                (4, 1): {'a': {(4, 2)}, 'f': {(4, 2)}, 'o': {(4, 2)}, 'd': {(4, 2)}},
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3)))
        )

        self.assertEqual(nfa, NFA.edit_distance(alphabet, 'food', 2))

        nice_nfa = NFA.edit_distance(set(string.ascii_lowercase), 'nice', 1)

        self.assertFalse(nice_nfa.accepts_input('food'))

        close_strings = [
            'anice', 'bice', 'dice', 'fice', 'ice', 'mice', 'nace', 'nice',
            'niche', 'nick', 'nide', 'niece', 'nife', 'nile', 'nine', 'niue',
            'pice', 'rice', 'sice', 'tice', 'unice', 'vice', 'wice'
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(alphabet, 'food', -1)
        with self.assertRaises(ValueError):
            _ = NFA.edit_distance(alphabet, 'food', 2, insertion=False, deletion=False, substitution=False)

    def test_nfa_hamming_distance(self):
        alphabet = {'f', 'o', 'd', 'a'}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {'f': {(1, 0), (1, 1)}, 'd': {(1, 1)}, 'o': {(1, 1)}, 'a': {(1, 1)}},
                (0, 1): {'f': {(1, 1), (1, 2)}, 'd': {(1, 2)}, 'o': {(1, 2)}, 'a': {(1, 2)}},
                (0, 2): {'f': {(1, 2)}},
                (1, 0): {'o': {(2, 0), (2, 1)}, 'd': {(2, 1)}, 'a': {(2, 1)}, 'f': {(2, 1)}},
                (1, 1): {'o': {(2, 1), (2, 2)}, 'd': {(2, 2)}, 'a': {(2, 2)}, 'f': {(2, 2)}},
                (1, 2): {'o': {(2, 2)}},
                (2, 0): {'o': {(3, 1), (3, 0)}, 'd': {(3, 1)}, 'a': {(3, 1)}, 'f': {(3, 1)}},
                (2, 1): {'o': {(3, 1), (3, 2)}, 'd': {(3, 2)}, 'a': {(3, 2)}, 'f': {(3, 2)}},
                (2, 2): {'o': {(3, 2)}},
                (3, 0): {'d': {(4, 0), (4, 1)}, 'o': {(4, 1)}, 'a': {(4, 1)}, 'f': {(4, 1)}},
                (3, 1): {'d': {(4, 1), (4, 2)}, 'o': {(4, 2)}, 'a': {(4, 2)}, 'f': {(4, 2)}},
                (3, 2): {'d': {(4, 2)}},
                (4, 0): {},
                (4, 1): {},
                (4, 2): {}
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3)))
        )

        self.assertEqual(nfa, NFA.edit_distance(alphabet, 'food', 2, insertion=False, deletion=False))

        nice_nfa = NFA.edit_distance(set(string.ascii_lowercase), 'nice', 1, insertion=False, deletion=False)

        self.assertFalse(nice_nfa.accepts_input('food'))

        close_strings = [
            'bice', 'dice', 'fice', 'mice', 'nace', 'nice',
            'nick', 'nide', 'nife', 'nile', 'nine', 'niue',
            'pice', 'rice', 'sice', 'tice', 'vice', 'wice'
        ]

        for close_string in close_strings:
            self.assertTrue(nice_nfa.accepts_input(close_string))

        close_strings_insertion_deletion = [
            'anice', 'nicee', 'niece', 'unice', 'niace', 'ice', 'nce', 'nic'
        ]

        for close_string in close_strings_insertion_deletion:
            self.assertFalse(nice_nfa.accepts_input(close_string))

    def test_nfa_LCS_distance(self):
        alphabet = {'f', 'o', 'd', 'a'}

        nfa = NFA(
            states=set(product(range(5), range(4))),
            input_symbols=alphabet,
            transitions={
                (0, 0): {'f': {(1, 0), (0, 1)}, 'd': {(0, 1)}, 'a': {(0, 1)}, 'o': {(0, 1)}, '': {(1, 1)}},
                (0, 1): {'f': {(1, 1), (0, 2)}, 'd': {(0, 2)}, 'a': {(0, 2)}, 'o': {(0, 2)}, '': {(1, 2)}},
                (0, 2): {'f': {(1, 2)}},
                (1, 0): {'o': {(1, 1), (2, 0)}, 'd': {(1, 1)}, 'a': {(1, 1)}, 'f': {(1, 1)}, '': {(2, 1)}},
                (1, 1): {'o': {(1, 2), (2, 1)}, 'd': {(1, 2)}, 'a': {(1, 2)}, 'f': {(1, 2)}, '': {(2, 2)}},
                (1, 2): {'o': {(2, 2)}},
                (2, 0): {'o': {(2, 1), (3, 0)}, 'd': {(2, 1)}, 'a': {(2, 1)}, 'f': {(2, 1)}, '': {(3, 1)}},
                (2, 1): {'o': {(3, 1), (2, 2)}, 'd': {(2, 2)}, 'a': {(2, 2)}, 'f': {(2, 2)}, '': {(3, 2)}},
                (2, 2): {'o': {(3, 2)}},
                (3, 0): {'d': {(3, 1), (4, 0)}, 'a': {(3, 1)}, 'f': {(3, 1)}, 'o': {(3, 1)}, '': {(4, 1)}},
                (3, 1): {'d': {(3, 2), (4, 1)}, 'a': {(3, 2)}, 'f': {(3, 2)}, 'o': {(3, 2)}, '': {(4, 2)}},
                (3, 2): {'d': {(4, 2)}},
                (4, 0): {'d': {(4, 1)}, 'a': {(4, 1)}, 'f': {(4, 1)}, 'o': {(4, 1)}},
                (4, 1): {'d': {(4, 2)}, 'a': {(4, 2)}, 'f': {(4, 2)}, 'o': {(4, 2)}}, (4, 2): {}
            },
            initial_state=(0, 0),
            final_states=set(product([4], range(3)))
        )

        self.assertEqual(nfa, NFA.edit_distance(alphabet, 'food', 2, substitution=False))

        close_strings_substitution = ['tice', 'nick', 'noce']
        close_strings_insertion = ['anice', 'nicee', 'niece', 'unice', 'niace']
        close_strings_deletion = ['ice', 'nce', 'nic']

        nice_nfa_insertion = NFA.edit_distance(set(string.ascii_lowercase), 'nice', 1,
                                               insertion=True, substitution=False, deletion=False)
        nice_nfa_deletion = NFA.edit_distance(set(string.ascii_lowercase), 'nice', 1,
                                              deletion=True, substitution=False, insertion=False)

        for close_string in close_strings_substitution:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_insertion:
            self.assertFalse(nice_nfa_deletion.accepts_input(close_string))
            self.assertTrue(nice_nfa_insertion.accepts_input(close_string))

        for close_string in close_strings_deletion:
            self.assertTrue(nice_nfa_deletion.accepts_input(close_string))
            self.assertFalse(nice_nfa_insertion.accepts_input(close_string))

    def test_nfa_shuffle_product(self):
        """
        Test shuffle product of two NFAs.

        Test cases based on https://planetmath.org/shuffleoflanguages
        """
        alphabet = {'a', 'b'}

        # Basic finite language test case
        nfa1 = NFA.from_dfa(DFA.from_finite_language(alphabet, {'aba'}))
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {'bab'}))

        nfa3 = NFA.from_dfa(DFA.from_finite_language(alphabet, {
            'abbaab', 'baabab', 'ababab', 'babaab', 'abbaba', 'baabba', 'ababba', 'bababa'
        }))

        self.assertEqual(nfa1.shuffle_product(nfa2), nfa3)

        # Regular language test case
        nfa4 = NFA.from_regex('aa', input_symbols=alphabet)
        nfa5 = NFA.from_regex('b*', input_symbols=alphabet)

        nfa6 = NFA.from_dfa(DFA.of_length(alphabet, min_length=2, max_length=2, symbols_to_count={'a'}))

        self.assertEqual(nfa4.shuffle_product(nfa5), nfa6)

        nfa7 = NFA.from_regex('a?a?a?')
        nfa8 = NFA.from_dfa(DFA.of_length(alphabet, max_length=3, symbols_to_count={'a'}))

        self.assertEqual(nfa5.shuffle_product(nfa7), nfa8)

        # raise error if other is not NFA
        with self.assertRaises(TypeError):
            self.nfa.shuffle_product(self.dfa)

    def test_nfa_shuffle_product_set_laws(self):
        """Test set laws for shuffle product"""
        alphabet = {'a', 'b'}

        # Language properties test case
        nfa1 = NFA.from_regex('a(a*b|b)', input_symbols=alphabet)
        nfa2 = NFA.from_regex('(aa+b)&(abbb)|(bba+)', input_symbols=alphabet)
        nfa3 = NFA.from_regex('a(a*b|b)b(ab*|ba*)', input_symbols=alphabet)

        # Commutativity
        self.assertEqual(nfa1.shuffle_product(nfa2), nfa2.shuffle_product(nfa1))
        # Associativity
        self.assertEqual(
            nfa1.shuffle_product(nfa2.shuffle_product(nfa3)),
            nfa1.shuffle_product(nfa2).shuffle_product(nfa3)
        )
        # Distributes over union
        self.assertEqual(
            nfa1.shuffle_product(nfa2.union(nfa3)),
            nfa1.shuffle_product(nfa2).union(nfa1.shuffle_product(nfa3))
        )

    def test_right_quotient(self):
        import string
        alphabet = set(string.ascii_lowercase)

        nfa1 = NFA.from_dfa(DFA.from_finite_language(alphabet, {'hooray', 'sunray', 'defray', 'ray'}))
        nfa2 = NFA.from_dfa(DFA.from_finite_language(alphabet, {'ray'}))

        equiv_dfa = DFA.from_nfa(nfa1.right_quotient(nfa2))
        print([word for word in equiv_dfa])
        #self.assertEqual(nfa1, nfa2)
