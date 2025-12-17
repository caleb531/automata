"""Classes and functions for testing the behavior of Regex tools"""

import re as regex
import string
import unittest

import automata.base.exceptions as exceptions
import automata.regex.regex as re
from automata.fa.nfa import NFA
from automata.regex.parser import StringToken, WildcardToken


class TestRegex(unittest.TestCase):
    """A test class for testing regular expression tools"""

    def test_validate_valid(self) -> None:
        """Should pass validation for valid regular expression"""
        re.validate("a*")
        re.validate("b|a?*")

    def test_validate_invalid(self) -> None:
        """Should raise error for invalid regular expressions"""
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "ab|")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "?")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a|b|*")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a||b")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "((abc*)))((abd)")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "*")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "ab(bc)*((bbcd)")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a(*)")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a(|)")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a{1,0}")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a{-1,}")
        self.assertRaises(exceptions.InvalidRegexError, re.validate, "a{-2,-1}")

    def test_invalid_token_creation(self) -> None:
        """Should raise error for invalid class creation"""
        match_obj = regex.compile("a").match("a")
        self.assertRaises(NotImplementedError, StringToken.from_match, match_obj)
        self.assertRaises(NotImplementedError, WildcardToken.from_match, match_obj)

    def test_helper_validate_invalid(self) -> None:
        """Should pass validation for valid regular expression"""
        self.assertFalse(re._validate("a(|)"))

    def test_validate_unicode_characters(self) -> None:
        """Should pass validation for regular expressions with unicode characters."""
        re.validate("(µ|🤖ù)*")

    def test_unicode_input_symbols(self) -> None:
        """Should have correct unicode input symbols."""
        nfa = NFA.from_regex("(µ🔥|🔥✨?)*")
        self.assertEqual(nfa.input_symbols, {"µ", "🔥", "✨"})

    def test_isequal(self) -> None:
        """Should correctly check equivalence of two regular expressions"""

        self.assertTrue(re.isequal("aa?", "a|aa"))
        self.assertTrue(re.isequal("a(a*b|b)", "aaa*b|ab"))
        self.assertTrue(
            re.isequal(
                "a(a*b|b)b(cd*|dc*)",
                "(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))",
            )
        )
        self.assertTrue(
            re.isequal(
                "(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))",
                "((aaaa*bbcd|aabbcd)d|abbcdd)d*|((aaaa*bb|aabb)dccc*|"
                "((aaaa*bbcd|aabbcd)|((aaaa*bb|aabb)(dc|(c|d))|(abbdccc*|(abb(dc|(c|d))|abbcd)))))",  # noqa
            )
        )

    def test_not_isequal(self) -> None:
        """Should correctly check non-equivalence of two regular expressions"""

        self.assertFalse(
            re.isequal(
                "baaa*b(b|a)|(bab(b|a)|(bb|ba))",
                "baaaa*b(a|b)|(baab(a|b)|bab(bb|(a|(b|ba))))",
            )
        )

    def test_issubset(self) -> None:
        """Should correctly verify if re1 is subset of re2"""

        self.assertTrue(re.issubset("aa?", "a*"))
        self.assertFalse(re.issubset("a*", "a?"))
        self.assertTrue(re.issubset("aaa*b|bc", "a*b|b*c*"))

    def test_issuperset(self) -> None:
        """Should correctly verify if re1 is superset of re2"""

        self.assertFalse(re.issuperset("aa?", "a*"))
        self.assertTrue(re.issuperset("a*", "a?"))
        self.assertTrue(re.issuperset("a*b|b*c*", "aaa*b|bc"))

    def test_intersection(self) -> None:
        """Should correctly check intersection of two regular expressions"""
        # Basic test
        nfa_1 = NFA.from_regex("(0|(01))&(01)")
        nfa_2 = NFA.from_regex("01")

        self.assertEqual(nfa_1, nfa_2)

        # Test intersection with NFA function on unrelated regexes
        regex_1 = "a|abacd"
        regex_2 = "a(a*b|b)b(cd*|dc*)"
        nfa_3 = NFA.from_regex(regex_1).intersection(NFA.from_regex(regex_2))
        nfa_4 = NFA.from_regex(f"({regex_1})&({regex_2})")

        self.assertEqual(nfa_3, nfa_4)

        # Test intersection subset
        regex_3 = "bcdaaa"
        nfa_5 = NFA.from_regex(regex_3)
        nfa_6 = NFA.from_regex(f"({regex_3})&(bcda*)")

        self.assertEqual(nfa_5, nfa_6)

        # Test distributive law
        regex_4 = f"{regex_1}&(({regex_2})|({regex_3}))"
        regex_5 = f"(({regex_1})&({regex_2}))|(({regex_1})&({regex_3}))"
        nfa_7 = NFA.from_regex(regex_4)
        nfa_8 = NFA.from_regex(regex_5)

        self.assertEqual(nfa_7, nfa_8)

    def test_kleene_plus(self) -> None:
        """Should correctly check kleene plus of two regular expressions"""
        # Basic test
        self.assertTrue(re.isequal("aa*", "a+"))
        self.assertTrue(re.isequal("(abc)(abc)*", "(abc)+"))
        self.assertTrue(re.isequal("a&a+", "a"))

        self.assertFalse(re.isequal("a*", "a+"))
        self.assertTrue(re.issuperset("a*", "a+"))

    def test_wildcard(self) -> None:
        """Should correctly check wildcard"""

        input_symbols = {"a", "b", "c"}

        self.assertTrue(re.isequal("a|b|c", ".", input_symbols=input_symbols))
        self.assertTrue(
            re.isequal("(abc)|(aac)|(acc)", "a.c", input_symbols=input_symbols)
        )
        self.assertTrue(re.isequal("a&.", "a", input_symbols=input_symbols))

        self.assertTrue(re.issubset("a.b", "...", input_symbols=input_symbols))
        self.assertTrue(re.issuperset(".", "a|b", input_symbols=input_symbols))

    def test_shuffle(self) -> None:
        """Should correctly check shuffle"""

        input_symbols = {"a", "b", "c", "d"}

        self.assertTrue(re.isequal("a^b", "ab|ba", input_symbols=input_symbols))
        self.assertTrue(
            re.isequal(
                "ab^cd",
                "abcd|acbd|cabd|acdb|cadb|cdab",
                input_symbols=input_symbols,
            )
        )
        self.assertTrue(
            re.isequal("(a*)^(b*)^(c*)^(d*)", ".*", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("ca^db", "(c^db)a|(ca^d)b", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("a^(b|c)", "ab|ac|ba|ca", input_symbols=input_symbols)
        )

        reference_nfa = NFA.from_regex("a*^ba")
        other_nfa = NFA.shuffle_product(NFA.from_regex("a*"), NFA.from_regex("ba"))
        self.assertEqual(reference_nfa, other_nfa)

    def test_quantifier(self) -> None:
        """Should correctly check quantifier"""

        input_symbols = {"a", "b", "c", "d"}

        # Simple equivalences
        self.assertTrue(re.isequal("a{1,3}", "a|aa|aaa", input_symbols=input_symbols))
        self.assertTrue(re.isequal("a{5,5}", "aaaaa", input_symbols=input_symbols))
        self.assertTrue(re.isequal("a{1,}", "a+", input_symbols=input_symbols))
        self.assertTrue(re.isequal("a{0,}", "a*", input_symbols=input_symbols))
        self.assertTrue(re.isequal("a{4,}", "aaaa+", input_symbols=input_symbols))
        self.assertTrue(
            re.isequal("a{,4}", "a?|aa|aaa|aaaa", input_symbols=input_symbols)
        )

        # More complex equivalences
        self.assertTrue(re.isequal("ba{,1}", "ba?", input_symbols=input_symbols))
        self.assertTrue(
            re.isequal("(b|a){0,2}", "(a?)|b|ab|ba|bb|aa", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("(a*b|b*c*){0,1}", "(a*b|b*c*)?", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal(
                "(aa^bb|ca^cb){0,}", "(aa^bb|ca^cb)*", input_symbols=input_symbols
            )
        )
        self.assertTrue(
            re.isequal(
                "(aa|bb^ca|cb){1,}", "(aa|bb^ca|cb)+", input_symbols=input_symbols
            )
        )

        # Tests for multiple quantifiers
        self.assertTrue(
            re.isequal("a{1,2}b{1,2}", "ab|aab|abb|aabb", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("a{2,2}(c*b){3,3}", "aac*bc*bc*b", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("a{2,2}ccb{3,3}", "aaccbbb", input_symbols=input_symbols)
        )

    def test_blank(self) -> None:
        """Should correctly parse blank"""
        self.assertTrue(re.isequal("()", ""))
        self.assertTrue(re.isequal("a|()", "a?"))
        self.assertTrue(re.isequal("a()", "a"))
        self.assertTrue(re.isequal("a()b()()c()", "abc"))

    def test_reserved_characters_handled_correctly(self) -> None:
        """Should throw exception if reserved character is in input symbols"""
        nfa = NFA.from_regex("a+", input_symbols={"a", "+"})
        self.assertTrue(nfa.accepts_input("a"))
        self.assertTrue(nfa.accepts_input("aa"))
        self.assertFalse(nfa.accepts_input("a+"))
        self.assertFalse(nfa.accepts_input(""))
        self.assertFalse(nfa.accepts_input("+"))

    def test_character_class(self) -> None:
        """Should correctly handle character classes"""
        # Basic equivalence
        self.assertTrue(re.isequal("[abc]", "a|b|c"))
        self.assertTrue(re.isequal("a[bc]d", "abd|acd"))
        # With NFA construction
        nfa1 = NFA.from_regex("[abc]")
        nfa2 = NFA.from_regex("a|b|c")
        self.assertEqual(nfa1, nfa2)
        # Character class with repetition
        self.assertTrue(re.isequal("[abc]*", "(a|b|c)*"))

        input_symbols = {"a", "b", "c", "d", "e"}
        # Simple range
        self.assertTrue(re.isequal("[a-c]", "a|b|c", input_symbols=input_symbols))
        # Multiple ranges
        self.assertTrue(re.isequal("[a-ce-e]", "a|b|c|e", input_symbols=input_symbols))
        # Range with individual characters
        self.assertTrue(re.isequal("[a-cd]", "a|b|c|d", input_symbols=input_symbols))
        # Create NFAs with negated character classes
        nfa1 = NFA.from_regex("[^abc]", input_symbols=input_symbols)
        nfa2 = NFA.from_regex("[^a-c]", input_symbols=input_symbols)
        nfa3 = NFA.from_regex("a[^abc]+", input_symbols=input_symbols)
        # Test acceptance/rejection patterns for simple negation
        self.assertTrue(nfa1.accepts_input("d"))
        self.assertTrue(nfa1.accepts_input("e"))
        self.assertFalse(nfa1.accepts_input("a"))
        self.assertFalse(nfa1.accepts_input("b"))
        self.assertFalse(nfa1.accepts_input("c"))
        # Test acceptance/rejection patterns for negated range
        self.assertTrue(nfa2.accepts_input("d"))
        self.assertTrue(nfa2.accepts_input("e"))
        self.assertFalse(nfa2.accepts_input("a"))
        self.assertFalse(nfa2.accepts_input("b"))
        self.assertFalse(nfa2.accepts_input("c"))
        # Test negated class with kleene plus
        self.assertTrue(nfa3.accepts_input("ad"))
        self.assertTrue(nfa3.accepts_input("ae"))
        self.assertTrue(nfa3.accepts_input("ade"))
        self.assertTrue(nfa3.accepts_input("aedd"))
        self.assertFalse(nfa3.accepts_input("a"))
        self.assertFalse(nfa3.accepts_input("aa"))
        self.assertFalse(nfa3.accepts_input("ab"))
        self.assertFalse(nfa3.accepts_input("abc"))

        # Test character class with provided input symbols
        nfa4 = NFA.from_regex("[a-zA-Z]+")
        self.assertTrue(nfa4.accepts_input("Hello"))
        self.assertTrue(nfa4.accepts_input("world"))
        self.assertFalse(nfa4.accepts_input("123"))
        self.assertFalse(nfa4.accepts_input("123abc"))
        self.assertFalse(nfa4.accepts_input("abc123"))

        input_symbols = {"a", "b", "c", "d", "e", "0", "1", "2", "3"}
        # Character class with quantifiers
        self.assertTrue(
            re.isequal(
                "[abc]{2}", "aa|ab|ac|ba|bb|bc|ca|cb|cc", input_symbols=input_symbols
            )
        )
        # Character class with operators
        self.assertTrue(
            re.isequal("[abc]|[0-3]", "a|b|c|0|1|2|3", input_symbols=input_symbols)
        )
        # Intersection with character classes
        self.assertTrue(re.isequal("[abc]&[bc0]", "b|c", input_symbols=input_symbols))
        # Shuffle with character classes
        self.assertTrue(
            re.isequal(
                "[ab]^[cd]", "ac|ad|bc|bd|ca|cb|da|db", input_symbols=input_symbols
            )
        )

        # Empty character class should raise error
        with self.assertRaises(exceptions.InvalidRegexError):
            re.validate("[]")
        # Special character as range boundary
        input_symbols = {"a", "b", "c", "-", "#"}
        self.assertTrue(re.isequal("[a-c-]", "a|b|c|-", input_symbols=input_symbols))
        # Hyphen at the beginning of class (literal interpretation)
        self.assertTrue(re.isequal("[-abc]", "-|a|b|c", input_symbols=input_symbols))
        # Hyphen at both beginning and end
        self.assertTrue(re.isequal("[-abc-]", "-|a|b|c", input_symbols=input_symbols))
        # Special character with literal interpretation
        input_symbols = {"a", "b", "c", "#"}
        self.assertTrue(re.isequal("[a#c]", "a|#|c", input_symbols=input_symbols))

        input_symbols = {"a", "b", "c"}
        # Exact repetition {n}
        self.assertTrue(
            re.isequal("[abc]{2}", "(a|b|c)(a|b|c)", input_symbols=input_symbols)
        )
        # Range repetition {n,m}
        self.assertTrue(
            re.isequal(
                "[abc]{1,2}", "(a|b|c)|(a|b|c)(a|b|c)", input_symbols=input_symbols
            )
        )
        # Lower bound only {n,}
        nfa1 = NFA.from_regex("[abc]{2,}", input_symbols=input_symbols)
        nfa2 = NFA.from_regex("(a|b|c)(a|b|c)((a|b|c)*)", input_symbols=input_symbols)
        self.assertEqual(nfa1, nfa2)

        # Test character class with reserved characters
        nfa1 = NFA.from_regex("[a+]")
        self.assertTrue(nfa1.accepts_input("a"))
        self.assertTrue(nfa1.accepts_input("+"))
        self.assertFalse(nfa1.accepts_input("b"))

        # One more more complex test with and without input symbols
        input_symbols = set(string.printable)
        nfa1 = NFA.from_regex("[a-zA-Z0-9._%+-]+", input_symbols=input_symbols)
        self.assertTrue(nfa1.accepts_input("a"))
        self.assertTrue(nfa1.accepts_input("1"))
        self.assertTrue(nfa1.accepts_input("."))
        self.assertTrue(nfa1.accepts_input("%"))
        self.assertTrue(nfa1.accepts_input("+"))
        self.assertFalse(nfa1.accepts_input(""))
        self.assertFalse(nfa1.accepts_input("$"))
        self.assertFalse(nfa1.accepts_input("{"))
        nfa2 = NFA.from_regex("[a-zA-Z0-9._%+-]+")
        self.assertTrue(nfa2.accepts_input("a"))
        self.assertTrue(nfa2.accepts_input("1"))
        self.assertTrue(nfa2.accepts_input("."))
        self.assertTrue(nfa2.accepts_input("%"))
        self.assertTrue(nfa2.accepts_input("+"))
        self.assertFalse(nfa2.accepts_input(""))
        self.assertFalse(nfa2.accepts_input("$"))
        self.assertFalse(nfa2.accepts_input("{"))

    def test_unicode_character_classes(self) -> None:
        """Should correctly handle Unicode character ranges in character classes"""

        def create_range(start_char: str, end_char: str) -> set[str]:
            return {chr(i) for i in range(ord(start_char), ord(end_char) + 1)}

        latin_ext_chars = create_range("\u00a1", "\u01bf")
        greek_chars = create_range("\u0370", "\u03ff")
        cyrillic_chars = create_range("\u0400", "\u04ff")

        input_symbols = set()
        input_symbols.update(latin_ext_chars)
        input_symbols.update(greek_chars)
        input_symbols.update(cyrillic_chars)

        ascii_chars = set(string.printable)
        input_symbols.update(ascii_chars)

        latin_nfa = NFA.from_regex("[\u00a1-\u01bf]+", input_symbols=input_symbols)
        greek_nfa = NFA.from_regex("[\u0370-\u03ff]+", input_symbols=input_symbols)
        cyrillic_nfa = NFA.from_regex("[\u0400-\u04ff]+", input_symbols=input_symbols)

        latin_samples = ["\u00a1", "\u00a3", "\u0100", "\u0155", "\u01bf"]
        greek_samples = ["\u0370", "\u0391", "\u0398", "\u03ff"]
        cyrillic_samples = ["\u0400", "\u0401", "\u040f", "\u04ff"]

        for char in latin_samples:
            self.assertTrue(latin_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(
            latin_nfa.accepts_input("\u00a1\u0100\u0155\u01bf")
        )  # Multiple characters
        self.assertFalse(latin_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(latin_nfa.accepts_input("\u0391"))  # Greek - not in range
        self.assertFalse(latin_nfa.accepts_input("\u0401"))  # Cyrillic - not in range
        self.assertFalse(latin_nfa.accepts_input("\u00a1a"))  # Mixed with non-matching

        for char in greek_samples:
            self.assertTrue(greek_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(
            greek_nfa.accepts_input("\u0370\u0391\u0398\u03ff")
        )  # Multiple characters
        self.assertFalse(greek_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(greek_nfa.accepts_input("\u0100"))  # Latin Ext - not in range
        self.assertFalse(greek_nfa.accepts_input("\u0401"))  # Cyrillic - not in range
        self.assertFalse(greek_nfa.accepts_input("\u0391a"))  # Mixed with non-matching

        for char in cyrillic_samples:
            self.assertTrue(cyrillic_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(
            cyrillic_nfa.accepts_input("\u0400\u0401\u040f\u04ff")
        )  # Multiple characters
        self.assertFalse(cyrillic_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(
            cyrillic_nfa.accepts_input("\u0100")
        )  # Latin Ext - not in range
        self.assertFalse(cyrillic_nfa.accepts_input("\u0391"))  # Greek - not in range
        self.assertFalse(
            cyrillic_nfa.accepts_input("\u0401a")
        )  # Mixed with non-matching

        combined_regex = (
            "Latin-Extension[\u00a1-\u01bf]+Greek[\u0370-\u03ff]+"
            "Cyrillic[\u0400-\u04ff]+"
        )
        combined_nfa = NFA.from_regex(combined_regex, input_symbols=input_symbols)

        self.assertTrue(
            combined_nfa.accepts_input("Latin-Extension\u00a1Greek\u0370Cyrillic\u0400")
        )
        self.assertTrue(
            combined_nfa.accepts_input(
                "Latin-Extension\u0100\u0101Greek\u0391\u0392\u0393Cyrillic\u0400\u0401\u0402"
            )
        )

        self.assertFalse(
            combined_nfa.accepts_input("Latin-ExtensionaGreek\u0370Cyrillic\u0400")
        )
        self.assertFalse(
            combined_nfa.accepts_input("Latin-Extension\u00a1GreekACyrillic\u0400")
        )
        self.assertFalse(
            combined_nfa.accepts_input("Latin-Extension\u00a1Greek\u0370CyrillicA")
        )

        non_latin_nfa = NFA.from_regex("[^\u00a1-\u01bf]+", input_symbols=input_symbols)
        self.assertTrue(non_latin_nfa.accepts_input("abc"))
        self.assertTrue(non_latin_nfa.accepts_input("\u0400\u0401\u040f\u04ff"))
        self.assertTrue(non_latin_nfa.accepts_input("\u0370\u0391\u0398"))
        self.assertFalse(non_latin_nfa.accepts_input("\u00a1"))
        self.assertFalse(non_latin_nfa.accepts_input("\u0100"))
        self.assertFalse(non_latin_nfa.accepts_input("a\u00a1"))

        alphabet = set("abcdefghijklmnopqrstuvwxyz")
        alphabet = alphabet
        safe_input_symbols = input_symbols.union(alphabet)

        ascii_range_nfa = NFA.from_regex("[i-p]+", input_symbols=safe_input_symbols)
        for char in "ijklmnop":
            self.assertTrue(
                ascii_range_nfa.accepts_input(char), f"Should accept {char}"
            )
        for char in "abcdefgh":
            self.assertFalse(
                ascii_range_nfa.accepts_input(char), f"Should reject {char}"
            )
        for char in "qrstuvwxyz":
            self.assertFalse(
                ascii_range_nfa.accepts_input(char), f"Should reject {char}"
            )

    def test_escape_characters(self) -> None:
        """Should correctly handle escape sequences in regex patterns"""
        # Basic escape sequences
        nfa_newline = NFA.from_regex("\\n")
        self.assertTrue(nfa_newline.accepts_input("\n"))
        self.assertFalse(nfa_newline.accepts_input("n"))
        self.assertFalse(nfa_newline.accepts_input("\\n"))

        nfa_carriage = NFA.from_regex("\\r")
        self.assertTrue(nfa_carriage.accepts_input("\r"))
        self.assertFalse(nfa_carriage.accepts_input("r"))

        nfa_tab = NFA.from_regex("\\t")
        self.assertTrue(nfa_tab.accepts_input("\t"))
        self.assertFalse(nfa_tab.accepts_input("t"))

        # Escaping special regex characters
        nfa_plus = NFA.from_regex("\\+")
        self.assertTrue(nfa_plus.accepts_input("+"))
        self.assertFalse(nfa_plus.accepts_input("\\+"))

        nfa_star = NFA.from_regex("\\*")
        self.assertTrue(nfa_star.accepts_input("*"))
        self.assertFalse(nfa_star.accepts_input("\\*"))

        # Multiple escape sequences
        nfa_multi = NFA.from_regex("\\n\\r\\t")
        self.assertTrue(nfa_multi.accepts_input("\n\r\t"))
        self.assertFalse(nfa_multi.accepts_input("\n\r"))

        # Character classes with escape sequences
        nfa_class = NFA.from_regex("[\\n\\r\\t]")
        self.assertTrue(nfa_class.accepts_input("\n"))
        self.assertTrue(nfa_class.accepts_input("\r"))
        self.assertTrue(nfa_class.accepts_input("\t"))
        self.assertFalse(nfa_class.accepts_input("n"))

        # Character class ranges with escape sequences
        nfa_range = NFA.from_regex("[\\n-\\r]")
        self.assertTrue(nfa_range.accepts_input("\n"))
        self.assertTrue(nfa_range.accepts_input("\r"))
        self.assertTrue(nfa_range.accepts_input("\013"))
        self.assertFalse(nfa_range.accepts_input("\t"))

        # Escape sequences with repetition operators
        nfa_repeat = NFA.from_regex("\\n+")
        self.assertTrue(nfa_repeat.accepts_input("\n"))
        self.assertTrue(nfa_repeat.accepts_input("\n\n"))
        self.assertTrue(nfa_repeat.accepts_input("\n\n\n"))
        self.assertFalse(nfa_repeat.accepts_input(""))

        # Complex patterns with escape sequences
        nfa_complex = NFA.from_regex("a\\nb+\\r(c|d)*")
        self.assertTrue(nfa_complex.accepts_input("a\nb\r"))
        self.assertTrue(nfa_complex.accepts_input("a\nbb\r"))
        self.assertTrue(nfa_complex.accepts_input("a\nb\rcd"))
        self.assertTrue(nfa_complex.accepts_input("a\nb\rcddc"))
        self.assertFalse(nfa_complex.accepts_input("anb\r"))

        # Backslash escaping itself
        nfa_backslash = NFA.from_regex("\\\\")
        self.assertTrue(nfa_backslash.accepts_input("\\"))
        self.assertFalse(nfa_backslash.accepts_input("\\\\"))

        # Testing another regex
        nfa_complex2 = NFA.from_regex("a\\nb+\\r(c|d)*")
        self.assertTrue(nfa_complex2.accepts_input("a\nb\r"))
        self.assertTrue(nfa_complex2.accepts_input("a\nbb\r"))
        self.assertTrue(nfa_complex2.accepts_input("a\nb\rcd"))
        self.assertTrue(nfa_complex2.accepts_input("a\nb\rcddc"))
        self.assertFalse(nfa_complex2.accepts_input("anb\r"))

        # Escaped whitespace in character classes
        nfa_whitespace = NFA.from_regex("[\\n\\r\\t ]+")
        self.assertTrue(nfa_whitespace.accepts_input("\n\r\t "))
        self.assertTrue(nfa_whitespace.accepts_input(" \n"))
        self.assertTrue(nfa_whitespace.accepts_input("\t\r"))
        self.assertFalse(nfa_whitespace.accepts_input("a"))

        # Common escape sequences with input symbols
        input_symbols = set("abc\n\r\t ")
        nfa_with_symbols = NFA.from_regex("a\\nb[\\r\\t]c", input_symbols=input_symbols)
        self.assertTrue(nfa_with_symbols.accepts_input("a\nb\rc"))
        self.assertTrue(nfa_with_symbols.accepts_input("a\nb\tc"))
        self.assertFalse(nfa_with_symbols.accepts_input("a\nbc"))

    def test_shorthand_character_classes(self) -> None:
        """Should correctly handle shorthand character classes"""

        # \s - Any whitespace character
        whitespace_nfa = NFA.from_regex("\\s+")
        self.assertTrue(whitespace_nfa.accepts_input(" "))
        self.assertTrue(whitespace_nfa.accepts_input("\t"))
        self.assertTrue(whitespace_nfa.accepts_input("\n"))
        self.assertTrue(whitespace_nfa.accepts_input("\r"))
        self.assertTrue(whitespace_nfa.accepts_input("\f"))  # form feed
        self.assertTrue(whitespace_nfa.accepts_input(" \t\n"))  # multiple whitespace
        self.assertFalse(whitespace_nfa.accepts_input("a"))
        self.assertFalse(whitespace_nfa.accepts_input("1"))
        self.assertFalse(whitespace_nfa.accepts_input("a "))  # contains non-whitespace

        # \S - Any non-whitespace character
        non_whitespace_nfa = NFA.from_regex("\\S+")
        self.assertTrue(non_whitespace_nfa.accepts_input("a"))
        self.assertTrue(non_whitespace_nfa.accepts_input("1"))
        self.assertTrue(non_whitespace_nfa.accepts_input("abc123"))
        self.assertTrue(non_whitespace_nfa.accepts_input("!@#$%^&*()"))
        self.assertFalse(non_whitespace_nfa.accepts_input(" "))
        self.assertFalse(non_whitespace_nfa.accepts_input("\t"))
        self.assertFalse(non_whitespace_nfa.accepts_input("a "))  # contains whitespace

        # \d - Any digit
        digit_nfa = NFA.from_regex("\\d+")
        self.assertTrue(digit_nfa.accepts_input("0"))
        self.assertTrue(digit_nfa.accepts_input("9"))
        self.assertTrue(digit_nfa.accepts_input("0123456789"))
        self.assertFalse(digit_nfa.accepts_input("a"))
        self.assertFalse(digit_nfa.accepts_input("a1"))  # contains non-digit

        # \D - Any non-digit
        non_digit_nfa = NFA.from_regex("\\D+")
        self.assertTrue(non_digit_nfa.accepts_input("a"))
        self.assertTrue(non_digit_nfa.accepts_input("xyz"))
        self.assertTrue(non_digit_nfa.accepts_input("!@#$%^&*()"))
        self.assertTrue(non_digit_nfa.accepts_input(" \t\n"))  # whitespace is non-digit
        self.assertFalse(non_digit_nfa.accepts_input("0"))
        self.assertFalse(non_digit_nfa.accepts_input("12345"))
        self.assertFalse(non_digit_nfa.accepts_input("a1"))  # contains digit

        # \w - Any word character (alphanumeric or underscore)
        word_nfa = NFA.from_regex("\\w+")
        self.assertTrue(word_nfa.accepts_input("a"))
        self.assertTrue(word_nfa.accepts_input("Z"))
        self.assertTrue(word_nfa.accepts_input("0"))
        self.assertTrue(word_nfa.accepts_input("_"))
        self.assertTrue(word_nfa.accepts_input("a1_Z"))
        self.assertFalse(word_nfa.accepts_input("!"))
        self.assertFalse(word_nfa.accepts_input(" "))
        self.assertFalse(word_nfa.accepts_input("a!"))  # contains non-word

        # \W - Any non-word character
        non_word_nfa = NFA.from_regex("\\W+")
        self.assertTrue(non_word_nfa.accepts_input("!"))
        self.assertTrue(non_word_nfa.accepts_input("@#$%^&*()"))
        self.assertTrue(non_word_nfa.accepts_input(" \t\n"))  # whitespace is non-word
        self.assertFalse(non_word_nfa.accepts_input("a"))
        self.assertFalse(non_word_nfa.accepts_input("Z"))
        self.assertFalse(non_word_nfa.accepts_input("0"))
        self.assertFalse(non_word_nfa.accepts_input("_"))
        self.assertFalse(non_word_nfa.accepts_input("!a"))  # contains word

        # Combinations
        mixed_nfa = NFA.from_regex("\\d+\\s+\\w+")
        self.assertTrue(mixed_nfa.accepts_input("123 abc"))
        self.assertTrue(mixed_nfa.accepts_input("456\t_7"))
        self.assertFalse(mixed_nfa.accepts_input("abc 123"))  # wrong order
        self.assertFalse(mixed_nfa.accepts_input("123abc"))  # missing whitespace

        # Inside character classes
        class_nfa = NFA.from_regex("[\\d\\s]+")
        self.assertTrue(class_nfa.accepts_input("123"))
        self.assertTrue(class_nfa.accepts_input(" \t\n"))
        self.assertTrue(class_nfa.accepts_input("1 2\t3\n"))
        self.assertFalse(class_nfa.accepts_input("a"))

        # With other escape sequences
        complex_nfa = NFA.from_regex("\\w+\\t\\d+\\n")
        self.assertTrue(complex_nfa.accepts_input("abc\t123\n"))
        self.assertTrue(complex_nfa.accepts_input("_\t0\n"))
        self.assertFalse(complex_nfa.accepts_input("abc 123\n"))  # space instead of tab
        self.assertFalse(complex_nfa.accepts_input("abc\t123"))  # missing newline

    def test_negated_class_with_period(self) -> None:
        """Test that negated character classes can match the period character"""

        # Create an NFA with a negated character class
        nfa = NFA.from_regex(r"[.]+.", input_symbols={"a"})
        self.assertTrue(nfa.accepts_input(".a"))
        self.assertFalse(nfa.accepts_input("<a"))

        # Create an NFA with a negated character class
        nfa = NFA.from_regex(r"[^<>]+", input_symbols={"a", "."})
        self.assertTrue(nfa.accepts_input("."))
        self.assertTrue(nfa.accepts_input("..."))

        nfa = NFA.from_regex(r"[^<>]+", input_symbols=set(string.printable))
        # This should match any character except < and >
        self.assertTrue(nfa.accepts_input("abc"))
        self.assertTrue(nfa.accepts_input("123"))
        self.assertTrue(nfa.accepts_input('!@#$%^&*()_+{}|:",./?`~'))

        # These should not match
        self.assertFalse(nfa.accepts_input("<"))
        self.assertFalse(nfa.accepts_input(">"))
        self.assertFalse(nfa.accepts_input("a<b"))  # contains <
        self.assertFalse(nfa.accepts_input("a>b"))  # contains >

    def test_slash_character(self) -> None:
        """Should correctly handle the slash character"""
        nfa = NFA.from_regex(r"/", input_symbols=set(string.printable))
        self.assertTrue(nfa.accepts_input("/"))
        self.assertFalse(nfa.accepts_input("a/b"))

    def test_email_like_regexes(self) -> None:
        """Should correctly handle email-like regexes"""
        input_symbols = set(string.printable)

        # Pattern for bracketed email content: ">content<something"
        bracketed_nfa = NFA.from_regex(r">[^<>]+<.*", input_symbols=input_symbols)
        self.assertTrue(bracketed_nfa.accepts_input(">user@example.com<"))
        self.assertTrue(bracketed_nfa.accepts_input(">John Doe<john@example.com"))
        self.assertFalse(bracketed_nfa.accepts_input("user@example.com"))  # missing >
        self.assertFalse(bracketed_nfa.accepts_input("><"))  # empty content

        # Pattern for "To:" header field
        to_header_nfa = NFA.from_regex(r"to:[^\r\n]+\r\n", input_symbols=input_symbols)
        self.assertTrue(to_header_nfa.accepts_input("to:user@example.com\r\n"))
        self.assertTrue(
            to_header_nfa.accepts_input(
                "to:Multiple Recipients <group@example.com>\r\n"
            )
        )
        self.assertFalse(
            to_header_nfa.accepts_input("to:user@example.com")
        )  # missing newline
        self.assertFalse(
            to_header_nfa.accepts_input("from:user@example.com\r\n")
        )  # wrong header

        # Pattern for "Subject:" header field
        subject_nfa = NFA.from_regex(
            r"\)subject:[^\r\n]+\r\n", input_symbols=input_symbols
        )
        self.assertTrue(subject_nfa.accepts_input(")subject:Hello World\r\n"))
        self.assertTrue(
            subject_nfa.accepts_input(")subject:Re: Meeting Tomorrow at 10AM\r\n")
        )
        self.assertFalse(
            subject_nfa.accepts_input("subject:Hello World\r\n")
        )  # missing )

        # Pattern for standard email address
        email_nfa = NFA.from_regex(
            r"[A-Za-z0-9!#$%&'*+=?\-\^_`{|}~.\/]+@[A-Za-z0-9.\-@]+",
            input_symbols=input_symbols,
        )
        self.assertTrue(email_nfa.accepts_input("user@example.com"))
        self.assertTrue(email_nfa.accepts_input("user.name+tag@sub.example-site.co.uk"))
        self.assertTrue(email_nfa.accepts_input("unusual!#$%&'*character@example.com"))
        self.assertFalse(email_nfa.accepts_input("@example.com"))  # missing local part
        self.assertFalse(email_nfa.accepts_input("user@"))  # missing domain

        # Pattern for DKIM signature with Base64 hash
        dkim_bh_nfa = NFA.from_regex(
            r"dkim-signature:([a-z]+=[^;]+; )+bh=[a-zA-Z0-9+/=]+;",
            input_symbols=input_symbols,
        )
        self.assertTrue(
            dkim_bh_nfa.accepts_input(
                "dkim-signature:v=1; a=rsa-sha256; bh=47DEQpj8HBSa+/TImW+5JCeuQeR;"
            )
        )
        self.assertTrue(
            dkim_bh_nfa.accepts_input(
                "dkim-signature:v=1; a=rsa-sha256; d=example.org; bh=base64+/hash=;"
            )
        )
        self.assertFalse(
            dkim_bh_nfa.accepts_input("dkim-signature:v=1; bh=;")
        )  # empty hash

        # Pattern for alternative email address format
        alt_email_nfa = NFA.from_regex(
            r"[A-Za-z0-9!#$%&'*+=?\-\^_`{|}~.\/@]+@[A-Za-z0-9.\-]+",
            input_symbols=input_symbols,
        )
        self.assertTrue(alt_email_nfa.accepts_input("user@example.com"))
        self.assertTrue(
            alt_email_nfa.accepts_input("user/dept@example.com")
        )  # with slash
        self.assertFalse(alt_email_nfa.accepts_input("user@"))  # missing domain

        # Pattern for "From:" header field
        from_header_nfa = NFA.from_regex(
            r"from:[^\r\n]+\r\n", input_symbols=input_symbols
        )
        self.assertTrue(from_header_nfa.accepts_input("from:sender@example.com\r\n"))
        self.assertTrue(
            from_header_nfa.accepts_input("from:John Doe <john@example.com>\r\n")
        )
        self.assertFalse(
            from_header_nfa.accepts_input("from:sender@example.com")
        )  # missing newline

        # Pattern for DKIM signature with timestamp
        dkim_time_nfa = NFA.from_regex(
            r"dkim-signature:([a-z]+=[^;]+; )+t=[0-9]+;", input_symbols=input_symbols
        )
        self.assertTrue(
            dkim_time_nfa.accepts_input(
                "dkim-signature:v=1; a=rsa-sha256; t=1623456789;"
            )
        )
        self.assertTrue(
            dkim_time_nfa.accepts_input(
                "dkim-signature:v=1; a=rsa-sha256; s=selector; t=1623456789;"
            )
        )
        self.assertFalse(
            dkim_time_nfa.accepts_input("dkim-signature:v=1; t=;")
        )  # empty timestamp

        # Pattern for Message-ID header
        msgid_nfa = NFA.from_regex(
            r"message-id:<[A-Za-z0-9=@\.\+_-]+>\r\n", input_symbols=input_symbols
        )
        self.assertTrue(msgid_nfa.accepts_input("message-id:<123abc@example.com>\r\n"))
        self.assertTrue(
            msgid_nfa.accepts_input("message-id:<msg-123.456@mail.example.co.uk>\r\n")
        )
        self.assertFalse(
            msgid_nfa.accepts_input("message-id:<invalid chars!>\r\n")
        )  # invalid chars
        self.assertFalse(
            msgid_nfa.accepts_input("message-id:<valid@example.com>")
        )  # missing newline

    def test_repeating_group_with_space(self) -> None:
        """Test a simpler version of the DKIM signature pattern to isolate the issue"""
        input_symbols = set(string.printable)

        # Try another variation without the space in the pattern
        no_space = NFA.from_regex(r"([a-z]+=[^;]+;)+", input_symbols=input_symbols)
        self.assertTrue(no_space.accepts_input("v=1;"))
        self.assertTrue(no_space.accepts_input("v=1;a=2;"))

        # Test with explicit space character instead of relying on character class
        explicit_space = NFA.from_regex(
            r"([a-z]+=[^;]+; )+", input_symbols=input_symbols
        )
        self.assertTrue(explicit_space.accepts_input("v=1; "))

        # Simplified version of the problematic pattern
        simple_repeat = NFA.from_regex(
            r"([a-z]+=[^;]+; )+", input_symbols=input_symbols
        )
        self.assertTrue(simple_repeat.accepts_input("v=1; "))
        self.assertTrue(simple_repeat.accepts_input("v=1; a=2; "))

        # Test the full pattern but simplified
        full_simple = NFA.from_regex(
            r"header:([a-z]+=[^;]+; )+value;", input_symbols=input_symbols
        )
        self.assertTrue(full_simple.accepts_input("header:v=1; value;"))
        self.assertTrue(full_simple.accepts_input("header:v=1; a=2; value;"))

    def test_space_in_patterns(self) -> None:
        """Test different patterns with spaces to isolate the issue"""
        input_symbols = set(string.printable)

        # Test 1: Basic pattern with space at the end
        basic = NFA.from_regex(r"a ", input_symbols=input_symbols)
        self.assertTrue(basic.accepts_input("a "))

        # Test 2: Character class with space
        with_class = NFA.from_regex(r"a[b ]", input_symbols=input_symbols)
        self.assertTrue(with_class.accepts_input("a "))
        self.assertTrue(with_class.accepts_input("ab"))

        # Test 3: Simple repetition with space
        simple_repeat = NFA.from_regex(r"(a )+", input_symbols=input_symbols)
        self.assertTrue(simple_repeat.accepts_input("a "))
        self.assertTrue(simple_repeat.accepts_input("a a "))

        # Test 4: Specific repeating pattern without the semicolon
        no_semicolon = NFA.from_regex(r"([a-z]+=. )+", input_symbols=input_symbols)
        self.assertTrue(no_semicolon.accepts_input("v=1 "))
        self.assertTrue(no_semicolon.accepts_input("v=1 a=2 "))

        # Test 5: With semicolon but space before
        space_before = NFA.from_regex(r"([a-z]+=[^;]+ ;)+", input_symbols=input_symbols)
        self.assertTrue(space_before.accepts_input("v=1 ;"))
        self.assertTrue(space_before.accepts_input("v=1 ;a=2 ;"))

        # Test 6: Space as part of negated class
        space_in_neg = NFA.from_regex(r"([a-z]+=[^; ]+;)+", input_symbols=input_symbols)
        self.assertTrue(space_in_neg.accepts_input("v=1;"))

        # Test 7: Bare minimum to reproduce
        minimal = NFA.from_regex(r"(a; )+", input_symbols=input_symbols)
        self.assertTrue(minimal.accepts_input("a; "))
        self.assertTrue(minimal.accepts_input("a; a; "))
