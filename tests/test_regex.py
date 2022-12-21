#!/usr/bin/env python3
"""Classes and functions for testing the behavior of Regex tools"""

import unittest

import automata.base.exceptions as exceptions
import automata.regex.regex as re
from automata.fa.nfa import NFA


class TestRegex(unittest.TestCase):
    """A test class for testing regular expression tools"""

    def test_validate_valid(self):
        """Should pass validation for valid regular expression"""
        self.assertTrue(re.validate('a*'))
        self.assertTrue(re.validate('b|a?*'))

    def test_validate_invalid(self):
        """Should raise error for invalid regular expressions"""
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'ab|')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, '?')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'a|b|*')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'a||b')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, '((abc*)))((abd)')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, '*')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'abcd()')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'ab(bc)*((bbcd)')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'a(*)')
        self.assertRaises(exceptions.InvalidRegexError, re.validate, 'a(|)')

    def test_helper_validate_invalid(self):
        """Should pass validation for valid regular expression"""
        self.assertFalse(re._validate('a(|)'))

    def test_isequal(self):
        """Should correctly check equivalence of two regular expressions"""

        self.assertTrue(re.isequal('aa?', 'a|aa'))
        self.assertTrue(re.isequal('a(a*b|b)', 'aaa*b|ab'))
        self.assertTrue(re.isequal('a(a*b|b)b(cd*|dc*)', '(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))'))
        self.assertTrue(re.isequal('(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))',
                                   '((aaaa*bbcd|aabbcd)d|abbcdd)d*|((aaaa*bb|aabb)dccc*|'
                                   '((aaaa*bbcd|aabbcd)|((aaaa*bb|aabb)(dc|(c|d))|(abbdccc*|(abb(dc|(c|d))|abbcd)))))'))

    def test_not_isequal(self):
        """Should correctly check non-equivalence of two regular expressions"""

        self.assertFalse(re.isequal('baaa*b(b|a)|(bab(b|a)|(bb|ba))',
                                    'baaaa*b(a|b)|(baab(a|b)|bab(bb|(a|(b|ba))))'))

    def test_issubset(self):
        """Should correctly verify if re1 is subset of re2"""

        self.assertTrue(re.issubset('aa?', 'a*'))
        self.assertFalse(re.issubset('a*', 'a?'))
        self.assertTrue(re.issubset('aaa*b|bc', 'a*b|b*c*'))

    def test_issuperset(self):
        """Should correctly verify if re1 is superset of re2"""

        self.assertFalse(re.issuperset('aa?', 'a*'))
        self.assertTrue(re.issuperset('a*', 'a?'))
        self.assertTrue(re.issuperset('a*b|b*c*', 'aaa*b|bc'))

    def test_intersection(self):
        """Should correctly check intersection of two regular expressions"""
        # Basic test
        nfa_1 = NFA.from_regex('(0|(01))&(01)')
        nfa_2 = NFA.from_regex('01')

        self.assertEqual(nfa_1, nfa_2)

        # Test intersection with NFA function on unrelated regexes
        regex_1 = 'a|abacd'
        regex_2 = 'a(a*b|b)b(cd*|dc*)'
        nfa_3 = NFA.from_regex(regex_1).intersection(NFA.from_regex(regex_2))
        nfa_4 = NFA.from_regex(f'({regex_1})&({regex_2})')

        self.assertEqual(nfa_3, nfa_4)

        # Test intersection subset
        regex_3 = 'bcdaaa'
        nfa_5 = NFA.from_regex(regex_3)
        nfa_6 = NFA.from_regex(f'({regex_3}) & (bcda*)')

        self.assertEqual(nfa_5, nfa_6)

        # Test distributive law
        regex_4 = f'{regex_1} & (({regex_2}) | ({regex_3}))'
        regex_5 = f'(({regex_1}) & ({regex_2})) | (({regex_1}) & ({regex_3}))'
        nfa_7 = NFA.from_regex(regex_4)
        nfa_8 = NFA.from_regex(regex_5)

        self.assertEqual(nfa_7, nfa_8)

    def test_kleene_plus(self):
        """Should correctly check kleene plus of two regular expressions"""
        # Basic test
        self.assertTrue(re.isequal('aa*', 'a+'))
        self.assertTrue(re.isequal('(abc)(abc)*', '(abc)+'))
        self.assertTrue(re.isequal('a&a+', 'a'))

        self.assertFalse(re.isequal('a*', 'a+'))
        self.assertTrue(re.issuperset('a*', 'a+'))

    def test_wildcard(self):
        """Should correctly check wildcard"""

        input_symbols = {'a', 'b', 'c'}

        self.assertTrue(re.isequal('a|b|c', '.', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(abc)|(aac)|(acc)', 'a.c', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a&.', 'a', input_symbols=input_symbols))

        self.assertTrue(re.issubset('a.b', '...', input_symbols=input_symbols))
        self.assertTrue(re.issuperset('.', 'a|b', input_symbols=input_symbols))

    def test_shuffle(self):
        """Should correctly check shuffle"""

        input_symbols = {'a', 'b', 'c', 'd'}

        self.assertTrue(re.isequal('a^b', 'ab|ba', input_symbols=input_symbols))
        self.assertTrue(re.isequal('ab^cd', 'abcd | acbd | cabd | acdb | cadb | cdab', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(a*)^(b*)^(c*)^(d*)', '.*', input_symbols=input_symbols))
        self.assertTrue(re.isequal('ca^db', '(c^db)a | (ca^d)b', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a^(b|c)', 'ab | ac | ba | ca', input_symbols=input_symbols))

        reference_nfa = NFA.from_regex('a*^ba')
        other_nfa = NFA.shuffle_product(NFA.from_regex('a*'), NFA.from_regex('ba'))
        self.assertEqual(reference_nfa, other_nfa)

    def test_quantifier(self):
        """Should correctly check shuffle"""

        input_symbols = {'a', 'b', 'c', 'd'}

        # Simple equivalences
        self.assertTrue(re.isequal('a{1,3}', 'a|aa|aaa', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a{5,5}', 'aaaaa', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a{1,}', 'a+', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a{0,}', 'a*', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a{4,}', 'aaaa+', input_symbols=input_symbols))
        self.assertTrue(re.isequal('a{,4}', 'a?|aa|aaa|aaaa', input_symbols=input_symbols))

        # More complex equivalences
        self.assertTrue(re.isequal('ba{,1}', 'ba?', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(b|a){0,2}', '(a?)|b|ab|ba|bb|aa', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(a*b|b*c*){0,1}', '(a*b|b*c*)?', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(aa^bb|ca^cb){0,}', '(aa^bb|ca^cb)*', input_symbols=input_symbols))
        self.assertTrue(re.isequal('(aa|bb^ca|cb){1,}', '(aa|bb^ca|cb)+', input_symbols=input_symbols))

    def test_invalid_symbols(self):
        """Should throw exception if reserved character is in input symbols"""
        with self.assertRaises(exceptions.InvalidSymbolError):
            NFA.from_regex('a+', input_symbols={'a', '+'})
