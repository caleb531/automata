#!/usr/bin/env python3
"""Classes and functions for testing the behavior of NFAs."""
import os
import tempfile
import types
from unittest.mock import patch

import automata.base.exceptions as exceptions
import tests.test_fa as test_fa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    temp_dir_path = tempfile.gettempdir()

    def test_init_nfa(self):
        """Should copy NFA if passed into NFA constructor."""
        new_nfa = NFA.copy(self.nfa)
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

    def test_nfa_hashable(self):
        self.assertIsInstance(hash(self.nfa), int)

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
        NFA.copy(self.nfa)
        validate.assert_called_once_with()

    def test_nfa_equal(self):
        """Should correctly determine if two NFAs are equal."""
        new_nfa = self.nfa.copy()
        self.assertTrue(self.nfa == new_nfa, 'NFAs are not equal')

    def test_nfa_not_equal(self):
        """Should correctly determine if two NFAs are not equal."""
        new_nfa = NFA(
            states={'q0'},
            input_symbols={'a'},
            transitions={
                'q0': {'a': {'q0'}}
            },
            initial_state='q0',
            final_states={'q0'}
        )
        self.assertTrue(self.nfa != new_nfa, 'NFAs are equal')

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
        self.assertEqual(self.nfa.accepts_input('aba'), True)

    def test_accepts_input_false(self):
        """Should return False if NFA input is rejected."""
        self.assertEqual(self.nfa.accepts_input('abba'), False)

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
        self.assertNotEqual(nfa.accepts_input(''), None)

    def test_operations_other_type(self):
        """Should raise NotImplementedError for concatenate."""
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
        with self.assertRaises(NotImplementedError):
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

        self.assertEqual(concat_nfa.accepts_input(''), False)
        self.assertEqual(concat_nfa.accepts_input('0'), False)
        self.assertEqual(concat_nfa.accepts_input('1'), True)
        self.assertEqual(concat_nfa.accepts_input('00'), False)
        self.assertEqual(concat_nfa.accepts_input('01'), True)
        self.assertEqual(concat_nfa.accepts_input('10'), True)
        self.assertEqual(concat_nfa.accepts_input('11'), True)
        self.assertEqual(concat_nfa.accepts_input('101'), True)
        self.assertEqual(concat_nfa.accepts_input('101100'), True)
        self.assertEqual(concat_nfa.accepts_input('1010'), True)

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
        self.assertEqual(kleene_nfa.accepts_input(''), True)
        self.assertEqual(kleene_nfa.accepts_input('a'), False)
        self.assertEqual(kleene_nfa.accepts_input('b'), False)
        self.assertEqual(kleene_nfa.accepts_input('aa'), True)
        self.assertEqual(kleene_nfa.accepts_input('ab'), True)
        self.assertEqual(kleene_nfa.accepts_input('ba'), False)
        self.assertEqual(kleene_nfa.accepts_input('bb'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaa'), False)
        self.assertEqual(kleene_nfa.accepts_input('aba'), False)
        self.assertEqual(kleene_nfa.accepts_input('abaa'), True)
        self.assertEqual(kleene_nfa.accepts_input('abba'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaa'), False)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaab'), True)
        self.assertEqual(kleene_nfa.accepts_input('aaabababaaaaba'), False)

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
        self.assertEqual(reverse_nfa.accepts_input('a'), False)
        self.assertEqual(reverse_nfa.accepts_input('ab'), False)
        self.assertEqual(reverse_nfa.accepts_input('ba'), True)
        self.assertEqual(reverse_nfa.accepts_input('bba'), True)
        self.assertEqual(reverse_nfa.accepts_input('bbba'), True)

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
        # convert them to dfa then check equivalence
        dfa1 = DFA.from_nfa(nfa1)
        dfa2 = DFA.from_nfa(nfa2)

        self.assertEqual(dfa1, dfa2)

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
        self.assertEqual(DFA.from_nfa(nfa1), DFA.from_nfa(original_nfa))
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
        self.assertNotEqual(nfa1.lambda_closures, original_nfa.lambda_closures)

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
        self.assertEqual(DFA.from_nfa(nfa1), DFA.from_nfa(original_nfa))

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
        self.assertNotEqual(nfa1.lambda_closures, original_nfa.lambda_closures)

    def test_eliminate_lambda_regex(self):
        nfa = NFA.from_regex('a(aaa*bbcd|abbcd)d*|aa*bb(dcc*|(d|c)b|a?bb(dcc*|(d|c)))ab(c|d)*(ccd)?')
        nfa_without_lambdas = nfa.eliminate_lambda()
        self.assertEqual(DFA.from_nfa(nfa), DFA.from_nfa(nfa_without_lambdas))

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
        dfa1 = DFA.from_nfa(nfa3)
        dfa2 = DFA.from_nfa(nfa4)

        self.assertEqual(dfa1, dfa2)
        # second check
        nfa5 = nfa1 | nfa2
        dfa3 = DFA.from_nfa(nfa5)

        self.assertEqual(dfa3, dfa2)

        # third check: union of NFA which is subset of other
        nfa6 = NFA.from_regex('aa*')
        nfa7 = NFA.from_regex('a*')
        nfa8 = nfa6.union(nfa7)
        nfa9 = nfa7.union(nfa6)
        self.assertEqual(DFA.from_nfa(nfa8), DFA.from_nfa(nfa7))
        self.assertEqual(DFA.from_nfa(nfa9), DFA.from_nfa(nfa7))

        # raise error if other is not NFA
        self.assertRaises(NotImplementedError, self.nfa.union, self.dfa)
        with self.assertRaises(NotImplementedError):
            self.nfa | self.dfa

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
