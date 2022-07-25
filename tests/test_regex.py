#!/usr/bin/env python3
"""Classes and functions for testing the behavior of RegEx tools"""

import unittest

import automata.base.regex as re
import automata.base.exceptions as exceptions


class TestRegEx(unittest.TestCase):
    """A test class for testing regular expression tools"""

    def test_validate(self):
        """Should raise error for invalid regular expressions"""
        self.assertRaises(exceptions.InvalidRegExError, re.validate, 'ab|')
        self.assertRaises(exceptions.InvalidRegExError, re.validate, '?')
        self.assertRaises(exceptions.InvalidRegExError, re.validate, 'a|b|*')
        self.assertRaises(exceptions.InvalidRegExError, re.validate, 'a||b')

    def test_isequal(self):
        """Should correctly check equivalence of two regular expressions"""

        self.assertTrue(re.isequal('aa?', 'a|aa'))
        self.assertTrue(re.isequal('a(a*b|b)', 'aaa*b|ab'))
        self.assertTrue(re.isequal('a(a*b|b)b(cd*|dc*)', '(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))'))
        self.assertTrue(re.isequal('(aaa*bbcd|abbcd)d*|(aaa*bb(dcc*|(d|c))|abb(dcc*|(d|c)))',
                                   '((aaaa*bbcd|aabbcd)d|abbcdd)d*|((aaaa*bb|aabb)dccc*|'
                                   '((aaaa*bbcd|aabbcd)|((aaaa*bb|aabb)(dc|(c|d))|(abbdccc*|(abb(dc|(c|d))|abbcd)))))'))

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



