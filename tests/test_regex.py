"""Classes and functions for testing the behavior of Regex tools"""

import re as regex
import string
import unittest

import automata.base.exceptions as exceptions
import automata.regex.regex as re
from automata.fa.nfa import NFA, RESERVED_CHARACTERS
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
        nfa_6 = NFA.from_regex(f"({regex_3}) & (bcda*)")

        self.assertEqual(nfa_5, nfa_6)

        # Test distributive law
        regex_4 = f"{regex_1} & (({regex_2}) | ({regex_3}))"
        regex_5 = f"(({regex_1}) & ({regex_2})) | (({regex_1}) & ({regex_3}))"
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
                "abcd | acbd | cabd | acdb | cadb | cdab",
                input_symbols=input_symbols,
            )
        )
        self.assertTrue(
            re.isequal("(a*)^(b*)^(c*)^(d*)", ".*", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("ca^db", "(c^db)a | (ca^d)b", input_symbols=input_symbols)
        )
        self.assertTrue(
            re.isequal("a^(b|c)", "ab | ac | ba | ca", input_symbols=input_symbols)
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

    def test_invalid_symbols(self) -> None:
        """Should throw exception if reserved character is in input symbols"""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA.from_regex("a+", input_symbols={"a", "+"})

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
        input_symbols = set(string.printable) - RESERVED_CHARACTERS
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

        def create_range(start_char, end_char):
            return {chr(i) for i in range(ord(start_char), ord(end_char) + 1)}

        latin_ext_chars = create_range("¡", "ƿ")
        greek_chars = create_range("Ͱ", "Ͽ")
        cyrillic_chars = create_range("Ѐ", "ӿ")

        input_symbols = set()
        input_symbols.update(latin_ext_chars)
        input_symbols.update(greek_chars)
        input_symbols.update(cyrillic_chars)

        ascii_chars = set(string.printable)
        input_symbols.update(ascii_chars)

        input_symbols = input_symbols - RESERVED_CHARACTERS

        latin_nfa = NFA.from_regex("[¡-ƿ]+", input_symbols=input_symbols)
        greek_nfa = NFA.from_regex("[Ͱ-Ͽ]+", input_symbols=input_symbols)
        cyrillic_nfa = NFA.from_regex("[Ѐ-ӿ]+", input_symbols=input_symbols)

        latin_samples = ["¡", "£", "Ā", "ŕ", "ƿ"]
        greek_samples = ["Ͱ", "Α", "Θ", "Ͽ"]
        cyrillic_samples = ["Ѐ", "Ё", "Џ", "ӿ"]

        for char in latin_samples:
            self.assertTrue(latin_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(latin_nfa.accepts_input("¡Āŕƿ"))  # Multiple characters
        self.assertFalse(latin_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(latin_nfa.accepts_input("Α"))  # Greek - not in range
        self.assertFalse(latin_nfa.accepts_input("Ё"))  # Cyrillic - not in range
        self.assertFalse(latin_nfa.accepts_input("¡a"))  # Mixed with non-matching

        for char in greek_samples:
            self.assertTrue(greek_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(greek_nfa.accepts_input("ͰΑΘϿ"))  # Multiple characters
        self.assertFalse(greek_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(greek_nfa.accepts_input("Ā"))  # Latin Ext - not in range
        self.assertFalse(greek_nfa.accepts_input("Ё"))  # Cyrillic - not in range
        self.assertFalse(greek_nfa.accepts_input("Αa"))  # Mixed with non-matching

        for char in cyrillic_samples:
            self.assertTrue(cyrillic_nfa.accepts_input(char), f"Should accept {char}")
        self.assertTrue(cyrillic_nfa.accepts_input("ЀЁЏӿ"))  # Multiple characters
        self.assertFalse(cyrillic_nfa.accepts_input("a"))  # ASCII - not in range
        self.assertFalse(cyrillic_nfa.accepts_input("Ā"))  # Latin Ext - not in range
        self.assertFalse(cyrillic_nfa.accepts_input("Α"))  # Greek - not in range
        self.assertFalse(cyrillic_nfa.accepts_input("Ёa"))  # Mixed with non-matching

        combined_regex = "Latin-Extension[¡-ƿ]+Greek[Ͱ-Ͽ]+Cyrillic[Ѐ-ӿ]+"
        combined_nfa = NFA.from_regex(combined_regex, input_symbols=input_symbols)

        self.assertTrue(combined_nfa.accepts_input("Latin-Extension¡GreekͰCyrillicЀ"))
        self.assertTrue(
            combined_nfa.accepts_input("Latin-ExtensionĀāGreekΑΒΓCyrillicЀЁЂ")
        )

        self.assertFalse(combined_nfa.accepts_input("Latin-ExtensionaGreekͰCyrillicЀ"))
        self.assertFalse(combined_nfa.accepts_input("Latin-Extension¡GreekACyrillicЀ"))
        self.assertFalse(combined_nfa.accepts_input("Latin-Extension¡GreekͰCyrillicA"))

        non_latin_nfa = NFA.from_regex("[^¡-ƿ]+", input_symbols=input_symbols)
        self.assertTrue(non_latin_nfa.accepts_input("abc"))
        self.assertTrue(non_latin_nfa.accepts_input("ЀЁЏӿ"))
        self.assertTrue(non_latin_nfa.accepts_input("ͰΑΘ"))
        self.assertFalse(non_latin_nfa.accepts_input("¡"))
        self.assertFalse(non_latin_nfa.accepts_input("Ā"))
        self.assertFalse(non_latin_nfa.accepts_input("a¡"))

        alphabet = set("abcdefghijklmnopqrstuvwxyz")
        alphabet = alphabet - RESERVED_CHARACTERS
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
