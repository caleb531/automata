"""Tests exercising DFA minimisation functionality."""

from automata.fa.dfa import DFA
from tests.test_dfa.base import DfaTestCase


class TestDfaMinify(DfaTestCase):
    """Validate DFA minimisation across varied constructions."""

    def test_minify_dfa(self) -> None:
        dfa = DFA(
            states={"q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q2"},
                "q1": {"0": "q3", "1": "q4"},
                "q2": {"0": "q5", "1": "q6"},
                "q3": {"0": "q3", "1": "q3"},
                "q4": {"0": "q4", "1": "q4"},
                "q5": {"0": "q5", "1": "q5"},
                "q6": {"0": "q6", "1": "q6"},
                "q7": {"0": "q7", "1": "q7"},
            },
            initial_state="q0",
            final_states={"q3", "q4", "q5", "q6"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(
            minimal_dfa.states,
            {
                frozenset(("q0",)),
                frozenset(("q1", "q2")),
                frozenset(("q3", "q4", "q5", "q6")),
            },
        )
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0",)): {
                    "0": frozenset(("q1", "q2")),
                    "1": frozenset(("q1", "q2")),
                },
                frozenset(("q1", "q2")): {
                    "0": frozenset(("q3", "q4", "q5", "q6")),
                    "1": frozenset(("q3", "q4", "q5", "q6")),
                },
                frozenset(("q3", "q4", "q5", "q6")): {
                    "0": frozenset(("q3", "q4", "q5", "q6")),
                    "1": frozenset(("q3", "q4", "q5", "q6")),
                },
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0",)))
        self.assertEqual(
            minimal_dfa.final_states, {frozenset(("q3", "q4", "q5", "q6"))}
        )

    def test_minify_dfa_complex(self) -> None:
        dfa = DFA(
            states={
                "13",
                "56",
                "18",
                "10",
                "15",
                "26",
                "24",
                "54",
                "32",
                "27",
                "5",
                "43",
                "8",
                "3",
                "17",
                "45",
                "57",
                "46",
                "35",
                "9",
                "0",
                "21",
                "39",
                "51",
                "6",
                "55",
                "47",
                "11",
                "20",
                "12",
                "59",
                "38",
                "44",
                "52",
                "16",
                "41",
                "1",
                "4",
                "28",
                "58",
                "48",
                "23",
                "22",
                "2",
                "31",
                "36",
                "34",
                "49",
                "40",
                "7",
                "25",
                "30",
                "53",
                "42",
                "33",
                "19",
                "50",
                "37",
                "14",
                "29",
            },
            input_symbols={"L", "U", "R", "D"},
            transitions={
                "55": {"L": "20", "U": "49", "R": "20", "D": "49"},
                "57": {"L": "5", "U": "6", "R": "1", "D": "46"},
                "35": {"L": "44", "U": "32", "R": "36", "D": "33"},
                "13": {"L": "45", "U": "23", "R": "45", "D": "23"},
                "43": {"L": "44", "U": "32", "R": "44", "D": "33"},
                "9": {"L": "5", "U": "6", "R": "1", "D": "6"},
                "53": {"L": "20", "U": "33", "R": "20", "D": "32"},
                "12": {"L": "40", "U": "23", "R": "25", "D": "11"},
                "42": {"L": "1", "U": "49", "R": "5", "D": "49"},
                "24": {"L": "40", "U": "48", "R": "25", "D": "23"},
                "27": {"L": "5", "U": "46", "R": "1", "D": "6"},
                "22": {"L": "40", "U": "48", "R": "25", "D": "11"},
                "19": {"L": "36", "U": "32", "R": "44", "D": "33"},
                "59": {"L": "40", "U": "48", "R": "45", "D": "11"},
                "39": {"L": "45", "U": "48", "R": "25", "D": "11"},
                "51": {"L": "20", "U": "18", "R": "20", "D": "18"},
                "34": {"L": "5", "U": "4", "R": "1", "D": "31"},
                "33": {"L": "44", "U": "0", "R": "36", "D": "28"},
                "23": {"L": "45", "U": "8", "R": "45", "D": "8"},
                "46": {"L": "44", "U": "0", "R": "44", "D": "28"},
                "58": {"L": "5", "U": "4", "R": "1", "D": "4"},
                "50": {"L": "20", "U": "28", "R": "20", "D": "0"},
                "54": {"L": "40", "U": "8", "R": "25", "D": "41"},
                "49": {"L": "1", "U": "18", "R": "5", "D": "18"},
                "21": {"L": "40", "U": "26", "R": "25", "D": "8"},
                "16": {"L": "5", "U": "31", "R": "1", "D": "4"},
                "6": {"L": "40", "U": "26", "R": "25", "D": "41"},
                "32": {"L": "36", "U": "0", "R": "44", "D": "28"},
                "48": {"L": "40", "U": "26", "R": "45", "D": "41"},
                "11": {"L": "45", "U": "26", "R": "25", "D": "41"},
                "15": {"L": "14", "U": "49", "R": "14", "D": "49"},
                "1": {"L": "56", "U": "6", "R": "37", "D": "46"},
                "3": {"L": "4", "U": "32", "R": "17", "D": "33"},
                "45": {"L": "8", "U": "23", "R": "8", "D": "23"},
                "52": {"L": "4", "U": "32", "R": "4", "D": "33"},
                "36": {"L": "56", "U": "6", "R": "37", "D": "6"},
                "20": {"L": "14", "U": "33", "R": "14", "D": "32"},
                "25": {"L": "47", "U": "23", "R": "10", "D": "11"},
                "29": {"L": "37", "U": "49", "R": "56", "D": "49"},
                "40": {"L": "47", "U": "48", "R": "10", "D": "23"},
                "5": {"L": "56", "U": "46", "R": "37", "D": "6"},
                "44": {"L": "47", "U": "48", "R": "10", "D": "11"},
                "38": {"L": "17", "U": "32", "R": "4", "D": "33"},
                "2": {"L": "47", "U": "48", "R": "8", "D": "11"},
                "30": {"L": "8", "U": "48", "R": "10", "D": "11"},
                "7": {"L": "14", "U": "18", "R": "14", "D": "18"},
                "37": {"L": "56", "U": "4", "R": "37", "D": "31"},
                "28": {"L": "4", "U": "0", "R": "17", "D": "28"},
                "8": {"L": "8", "U": "8", "R": "8", "D": "8"},
                "31": {"L": "4", "U": "0", "R": "4", "D": "28"},
                "17": {"L": "56", "U": "4", "R": "37", "D": "4"},
                "14": {"L": "14", "U": "28", "R": "14", "D": "0"},
                "10": {"L": "47", "U": "8", "R": "10", "D": "41"},
                "18": {"L": "37", "U": "18", "R": "56", "D": "18"},
                "47": {"L": "47", "U": "26", "R": "10", "D": "8"},
                "56": {"L": "56", "U": "31", "R": "37", "D": "4"},
                "4": {"L": "47", "U": "26", "R": "10", "D": "41"},
                "0": {"L": "17", "U": "0", "R": "4", "D": "28"},
                "26": {"L": "47", "U": "26", "R": "8", "D": "41"},
                "41": {"L": "8", "U": "26", "R": "10", "D": "41"},
            },
            initial_state="55",
            final_states={
                "15",
                "24",
                "54",
                "32",
                "27",
                "5",
                "43",
                "57",
                "3",
                "46",
                "35",
                "9",
                "21",
                "39",
                "51",
                "6",
                "55",
                "11",
                "20",
                "12",
                "59",
                "38",
                "44",
                "52",
                "16",
                "1",
                "58",
                "48",
                "22",
                "2",
                "36",
                "34",
                "49",
                "40",
                "25",
                "30",
                "53",
                "42",
                "33",
                "19",
                "50",
                "29",
            },
        )
        large_tuple = (
            "0",
            "10",
            "14",
            "17",
            "18",
            "23",
            "26",
            "28",
            "31",
            "37",
            "4",
            "41",
            "45",
            "47",
            "56",
            "8",
        )
        check_dfa = DFA(
            states={
                frozenset(("5",)),
                frozenset(("36",)),
                frozenset(("1",)),
                frozenset(("49",)),
                frozenset(("40",)),
                frozenset(("25",)),
                frozenset(("46",)),
                frozenset(("6",)),
                frozenset(("55",)),
                frozenset(large_tuple),
                frozenset(("33",)),
                frozenset(("11",)),
                frozenset(("20",)),
                frozenset(("48",)),
                frozenset(("44",)),
                frozenset(("32",)),
            },
            input_symbols={"L", "U", "R", "D"},
            transitions={
                frozenset(("48",)): {
                    "L": frozenset(("40",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("44",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("48",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("11",)),
                },
                frozenset(("40",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("48",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("33",)): {
                    "L": frozenset(("44",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("36",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("55",)): {
                    "L": frozenset(("20",)),
                    "U": frozenset(("49",)),
                    "R": frozenset(("20",)),
                    "D": frozenset(("49",)),
                },
                frozenset(("32",)): {
                    "L": frozenset(("36",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("44",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("46",)): {
                    "L": frozenset(("44",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("44",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("25",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("11",)),
                },
                frozenset(("6",)): {
                    "L": frozenset(("40",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("25",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("11",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("25",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(("5",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("46",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("6",)),
                },
                frozenset(("49",)): {
                    "L": frozenset(("1",)),
                    "U": frozenset(large_tuple),
                    "R": frozenset(("5",)),
                    "D": frozenset(large_tuple),
                },
                frozenset(large_tuple): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(large_tuple),
                    "R": frozenset(large_tuple),
                    "D": frozenset(large_tuple),
                },
                frozenset(("20",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("33",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("32",)),
                },
                frozenset(("36",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("6",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("6",)),
                },
                frozenset(("1",)): {
                    "L": frozenset(large_tuple),
                    "U": frozenset(("6",)),
                    "R": frozenset(large_tuple),
                    "D": frozenset(("46",)),
                },
            },
            initial_state=frozenset(("55",)),
            final_states={
                frozenset(("5",)),
                frozenset(("1",)),
                frozenset(("36",)),
                frozenset(("49",)),
                frozenset(("40",)),
                frozenset(("25",)),
                frozenset(("46",)),
                frozenset(("6",)),
                frozenset(("55",)),
                frozenset(("33",)),
                frozenset(("11",)),
                frozenset(("20",)),
                frozenset(("48",)),
                frozenset(("44",)),
                frozenset(("32",)),
            },
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, check_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, check_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, check_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, check_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, check_dfa.final_states)

    def test_minify_minimal_dfa(self) -> None:
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={"q0": {"0": "q0", "1": "q1"}, "q1": {"0": "q0", "1": "q1"}},
            initial_state="q0",
            final_states={"q1"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        other_minimal_dfa = DFA(
            states={frozenset(("q0",)), frozenset(("q1",))},
            input_symbols={"0", "1"},
            transitions={
                frozenset(("q0",)): {"0": frozenset(("q0",)), "1": frozenset(("q1",))},
                frozenset(("q1",)): {"0": frozenset(("q0",)), "1": frozenset(("q1",))},
            },
            initial_state=frozenset(("q0",)),
            final_states={frozenset(("q1",))},
        )

        self.assertEqual(minimal_dfa.states, other_minimal_dfa.states)
        self.assertEqual(minimal_dfa.input_symbols, other_minimal_dfa.input_symbols)
        self.assertEqual(minimal_dfa.transitions, other_minimal_dfa.transitions)
        self.assertEqual(minimal_dfa.initial_state, other_minimal_dfa.initial_state)
        self.assertEqual(minimal_dfa.final_states, other_minimal_dfa.final_states)

    def test_minify_dfa_initial_state(self) -> None:
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q0", "1": "q0"},
            },
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(("q0", "q1"))})
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q0", "q1")),
                }
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0", "q1")))
        self.assertEqual(minimal_dfa.final_states, {frozenset(("q0", "q1"))})

    def test_minify_dfa_no_final_states(self) -> None:
        dfa = DFA(
            states={"q0", "q1"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": "q1", "1": "q1"},
                "q1": {"0": "q0", "1": "q0"},
            },
            initial_state="q0",
            final_states=set(),
        )
        minimal_dfa = dfa.minify(retain_names=True)
        self.assertEqual(minimal_dfa.states, {frozenset(("q0", "q1"))})
        self.assertEqual(minimal_dfa.input_symbols, {"0", "1"})
        self.assertEqual(
            minimal_dfa.transitions,
            {
                frozenset(("q0", "q1")): {
                    "0": frozenset(("q0", "q1")),
                    "1": frozenset(("q0", "q1")),
                },
            },
        )
        self.assertEqual(minimal_dfa.initial_state, frozenset(("q0", "q1")))
        self.assertEqual(minimal_dfa.final_states, set())

    def test_minify_partial_dfa(self) -> None:
        partial_dfa_extra_state = DFA(
            states=set(range(5)),
            input_symbols={"0", "1"},
            transitions={0: {"1": 1, "0": 4}, 1: {"1": 2}, 2: {"1": 3}, 3: {}, 4: {}},
            initial_state=0,
            final_states={3},
            allow_partial=True,
        )

        minified_partial_dfa = partial_dfa_extra_state.minify()
        self.assertEqual(len(minified_partial_dfa.states), 4)
        self.assertEqual(minified_partial_dfa, partial_dfa_extra_state)

    def test_minify_partial_dfa_correctness(self) -> None:
        input_symbols = {"a", "b", "c"}
        dfa = DFA.from_finite_language(
            language={"ab", "abcb"}, input_symbols=input_symbols, as_partial=True
        )

        self.assertEqual(dfa.minify(), dfa)

        dfa2 = DFA.from_finite_language(
            language={"ab", "abba", "cbab"},
            input_symbols=input_symbols,
            as_partial=True,
        )

        self.assertEqual(dfa2.minify(), dfa2)

        self.assertEqual(dfa.union(dfa2, minify=False), dfa.union(dfa2, minify=True))
        self.assertEqual(
            dfa.intersection(dfa2, minify=False), dfa.intersection(dfa2, minify=True)
        )
        self.assertEqual(
            dfa.symmetric_difference(dfa2, minify=False),
            dfa.symmetric_difference(dfa2, minify=True),
        )
        self.assertEqual(
            dfa.difference(dfa2, minify=False), dfa.difference(dfa2, minify=True)
        )


__all__ = ["TestDfaMinify"]
