import unittest

from Vintageous.ex.parsers.s_cmd import SubstituteLexer
from Vintageous.ex.parsers.parsing import RegexToken
from Vintageous.ex.parsers.parsing import Lexer
from Vintageous.ex.parsers.parsing import EOF


class TestRegexToken(unittest.TestCase):
    def setUp(self):
        self.token = RegexToken("f[o]+")

    def testCanTestMembership(self):
        self.assertTrue("fo" in self.token)
        self.assertTrue("foo" in self.token)

    def testCanTestEquality(self):
        self.assertTrue("fo" == self.token)


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def testEmptyInputSetsCursorToEOF(self):
        self.lexer.parse('')
        self.assertEqual(self.lexer.c, EOF)

    def testDoesReset(self):
        c, cursor, string = self.lexer.c, self.lexer.cursor, self.lexer.string
        self.lexer.parse('')
        self.lexer._reset()
        self.assertEqual(c, self.lexer.c)
        self.assertEqual(cursor, self.lexer.cursor)
        self.assertEqual(string, self.lexer.string)

    def testCursorIsPrimed(self):
        self.lexer.parse("foo")
        self.assertEqual(self.lexer.c, 'f')

    def testCanConsume(self):
        self.lexer.parse("foo")
        self.lexer.consume()
        self.assertEqual(self.lexer.c, 'o')
        self.assertEqual(self.lexer.cursor, 1)

    def testCanReachEOF(self):
        self.lexer.parse("f")
        self.lexer.consume()
        self.assertEqual(self.lexer.c, EOF)

    def testPassingInJunk(self):
        self.assertRaises(TypeError, self.lexer.parse, 100)
        self.assertRaises(TypeError, self.lexer.parse, [])


class TestSubstituteLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = SubstituteLexer()

    def testCanParseEmptyInput(self):
        actual = self.lexer.parse('')

        self.assertEqual(actual, ['', ''])

    def testCanParseShortFormWithFlagsOnly(self):
        one_flag = self.lexer.parse(r'g')
        many_flags = self.lexer.parse(r'gi')

        self.assertEqual(one_flag, ['g', ''])
        self.assertEqual(many_flags, ['gi', ''])

    def testCanParseShortFormWithCountOnly(self):
        actual = self.lexer.parse(r'100')

        self.assertEqual(actual, ['', '100'])

    def testCanParseShortFormWithFlagsAndCount(self):
        actual_1 = self.lexer.parse(r'gi100')
        actual_2 = self.lexer.parse(r'  gi  100  ')

        self.assertEqual(actual_1, ['gi', '100'])
        self.assertEqual(actual_2, ['gi', '100'])

    def testThrowErrorIfCountIsFollowedByAnything(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"100gi")

    def testThrowErrorIfShortFormIsFollowedByAnythingOtherThanFlagsOrCount(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"x")

    def testCanParseOneSeparatorOnly(self):
        actual = self.lexer.parse(r"/")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseTwoSeparatorsOnly(self):
        actual = self.lexer.parse(r"//")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseThreeSeparatorsOnly(self):
        actual = self.lexer.parse(r"///")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseOnlySearchPattern(self):
        actual = self.lexer.parse(r"/foo")

        self.assertEqual(actual, ['foo', '', '', ''])

    def testCanParseOnlyReplacementString(self):
        actual = self.lexer.parse(r"//foo")

        self.assertEqual(actual, ['', 'foo', '', ''])

    def testCanParseOnlyFlags(self):
        actual = self.lexer.parse(r"///gi")

        self.assertEqual(actual, ['', '', 'gi', ''])

    def testCanParseOnlyCount(self):
        actual = self.lexer.parse(r"///100")

        self.assertEqual(actual, ['', '', '', '100'])

    def testCanParseOnlyFlagsAndCount(self):
        actual = self.lexer.parse(r"///gi100")

        self.assertEqual(actual, ['', '', 'gi', '100'])

    def testThrowIfFlagsAndCountAreReversed(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"///100gi")

    def testThrowIfFlagsAndCountAreInvalid(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"///x")

    def testCanEscapeDelimiter(self):
        actual = self.lexer.parse(r"/foo\/")

        self.assertEqual(actual, ['foo/', '', '', ''])

    def testCanEscapeDelimiterComplex(self):
        actual = self.lexer.parse(r"/foo\//hello")

        self.assertEqual(actual, ['foo/', 'hello', '', ''])
