"""NFA construction from regexes and lambda-elimination tests."""

import automata.base.exceptions as exceptions
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from tests.test_nfa.base import NfaTestCase


class TestNfaRegexConversions(NfaTestCase):
    """Validate regex-based construction and related transformations."""

    def test_from_regex(self) -> None:
        input_symbols = {"a", "b", "c", "d"}
        nfa1 = NFA.from_regex("ab(cd*|dc)|a?", input_symbols=input_symbols)
        nfa2 = NFA(
            states={0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
            input_symbols=input_symbols,
            initial_state=0,
            transitions={
                0: {"": {1, 10}},
                1: {"a": {2}},
                2: {"b": {3}},
                3: {"": {4, 7}},
                4: {"d": {5}},
                5: {"c": {6}},
                7: {"c": {8}},
                8: {"d": {9}},
                9: {"d": {9}},
                10: {"a": {11}},
            },
            final_states={6, 8, 9, 10, 11},
        )

        self.assertEqual(nfa1, nfa2)

    def test_from_regex_empty_string(self) -> None:
        NFA.from_regex("")

    def test_eliminate_lambda(self) -> None:
        original_nfa = NFA(
            states={0, 1, 2, 3, 4, 5, 6},
            initial_state=0,
            input_symbols={"a", "b", "c"},
            transitions={
                0: {"a": {1}},
                1: {"": {2, 6}, "b": {2}},
                2: {"": {4}, "c": {3}},
                4: {"a": {5}},
            },
            final_states={3, 6},
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)
        nfa2 = NFA(
            states={0, 1, 2, 3, 5},
            initial_state=0,
            input_symbols={"a", "b", "c"},
            transitions={
                0: {"a": {1}},
                1: {"a": {5}, "b": {2}, "c": {3}},
                2: {"a": {5}, "c": {3}},
            },
            final_states={1, 3},
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(
            nfa1._get_lambda_closures(), original_nfa._get_lambda_closures()
        )

    def test_eliminate_lambda_other(self) -> None:
        original_nfa = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={"a", "b"},
            transitions={0: {"a": {1}}, 1: {"": {2}, "b": {1}}, 2: {"b": {2}}},
            final_states={2},
        )
        nfa1 = original_nfa.eliminate_lambda()
        self.assertEqual(nfa1, original_nfa)

        nfa2 = NFA(
            states={0, 1, 2},
            initial_state=0,
            input_symbols={"a", "b"},
            transitions={0: {"a": {1}}, 1: {"b": {1, 2}}, 2: {"b": {2}}},
            final_states={1, 2},
        )

        self.assertEqual(nfa1.states, nfa2.states)
        self.assertEqual(nfa1.initial_state, nfa2.initial_state)
        self.assertEqual(nfa1.transitions, nfa2.transitions)
        self.assertEqual(nfa1.final_states, nfa2.final_states)
        self.assertEqual(nfa1.input_symbols, nfa2.input_symbols)
        self.assertNotEqual(
            nfa1._get_lambda_closures(), original_nfa._get_lambda_closures()
        )

    def test_eliminate_lambda_regex(self) -> None:
        nfa = NFA.from_regex(
            "a(aaa*bbcd|abbcd)d*|aa*bb(dcc*|(d|c)b|a?bb(dcc*|(d|c)))ab(c|d)*(ccd)?"
        )
        nfa_without_lambdas = nfa.eliminate_lambda()
        self.assertEqual(nfa, nfa_without_lambdas)

        for transition in nfa_without_lambdas.transitions.values():
            for char in transition.keys():
                self.assertNotEqual(char, "")

    def test_validate_regex(self) -> None:
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "ab|")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "?")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a|b|*")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a||b")
        self.assertRaises(
            exceptions.InvalidRegexError, NFA.from_regex, "((abc*)))((abd)"
        )
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "*")
        self.assertRaises(
            exceptions.InvalidRegexError, NFA.from_regex, "ab(bc)*((bbcd)"
        )
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "a(*)")
        self.assertRaises(exceptions.InvalidRegexError, NFA.from_regex, "ab(|)")

    def test_add_new_state_type_integrity(self) -> None:
        dfa1 = NFA(
            states={"0", "1"},
            input_symbols={"0"},
            transitions={"0": {"0": {"1"}}, "1": {"0": {"1"}}},
            initial_state="0",
            final_states={"1"},
        )

        dfa2 = DFA.from_nfa(dfa1.reverse())

        self.assertEqual(
            dfa1.accepts_input("00"),
            dfa2.accepts_input("00"),
            "DFA and NFA are not equivalent when they should be",
        )

    def test_nfa_equality(self) -> None:
        input_symbols = {"0", "1"}
        nfa1 = NFA(
            states={"s", "a", "b", "c", "d", "e", "f", "g", "h"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"g"}, "1": {"a"}},
                "a": {"0": {"b"}, "": {"d"}},
                "b": {"1": {"c"}},
                "c": {"0": {"a"}},
                "d": {"1": {"e"}, "": {"f"}},
                "e": {"1": {"d"}},
                "f": {"": {"s"}},
                "g": {"1": {"h"}},
                "h": {"0": {"f"}},
            },
            initial_state="s",
            final_states={"s"},
        )

        self.assertEqual(
            nfa1,
            NFA.from_regex("((1(010)*(11)*)|(010))*", input_symbols=input_symbols),
        )

        nfa2 = NFA(
            states={"s", "a", "b", "c", "d", "e"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"a"}, "1": {"s"}, "": {"b", "d"}},
                "a": {"1": {"s"}},
                "b": {"0": {"b"}, "1": {"c"}},
                "c": {"0": {"c"}, "1": {"e"}},
                "d": {"0": {"c"}, "1": {"d"}},
                "e": {"0": {"c"}},
            },
            initial_state="s",
            final_states={"c"},
        )

        self.assertEqual(
            nfa2,
            NFA.from_regex(
                "(((01) | 1)*)((0*1) | (1*0))(((10) | 0)*)",
                input_symbols=input_symbols,
            ),
        )

        nfa3 = NFA(
            states={"s", "0", "1", "00", "01", "10", "11"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"0"}, "1": {"1"}},
                "0": {"0": {"00"}, "1": {"01"}},
                "1": {"0": {"10"}, "1": {"11"}},
                "00": {"0": {"00"}, "1": {"01"}},
                "01": {"0": {"00"}, "1": {"01"}},
                "10": {"0": {"10"}, "1": {"11"}},
                "11": {"0": {"10"}, "1": {"11"}},
            },
            initial_state="s",
            final_states={"00", "11"},
        )

        self.assertEqual(
            nfa3,
            NFA.from_regex(
                "(0(0 | 1)*0) | (1(0 | 1)*1)",
                input_symbols=input_symbols,
            ),
        )

        nfa4 = NFA(
            states={"s", "0", "1", "00", "01", "10", "11"},
            input_symbols=input_symbols,
            transitions={
                "s": {"0": {"0"}, "1": {"1"}},
                "0": {"0": {"00"}, "1": {"01"}},
                "1": {"0": {"10"}, "1": {"11"}},
                "00": {"0": {"00"}, "1": {"01"}},
                "01": {"0": {"10"}, "1": {"11"}},
                "10": {"0": {"00"}, "1": {"01"}},
                "11": {"0": {"10"}, "1": {"11"}},
            },
            initial_state="s",
            final_states={"00", "11"},
        )

        self.assertEqual(
            nfa4,
            NFA.from_regex(
                "((0 | 1)*00) | ((0 | 1)*11)",
                input_symbols=input_symbols,
            ),
        )

        input_symbols_2 = {"0", "1", "2"}
        nfa5 = NFA(
            states={"s", "a", "b", "c", "d", "e", "f", "g", "h"},
            input_symbols=input_symbols_2,
            transitions={
                "s": {"": {"a", "f", "g"}, "2": {"c"}},
                "a": {"0": {"b", "c"}},
                "b": {"1": {"a"}},
                "c": {"1": {"s", "d"}},
                "d": {"0": {"e"}},
                "e": {"0": {"c"}},
                "f": {"1": {"f"}},
                "g": {"0": {"g"}, "": {"h"}},
                "h": {"2": {"h"}},
            },
            initial_state="s",
            final_states={"f", "h"},
        )

        self.assertEqual(
            nfa5,
            NFA.from_regex(
                "((((01)*0) | 2)(100)*1)*(1* | (0*2*))",
                input_symbols=input_symbols_2,
            ),
        )


__all__ = ["TestNfaRegexConversions"]
