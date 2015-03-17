import unittest

from Vintageous.ex.parsers.new.parser import start_parsing
from Vintageous.ex.parsers.new.scanner import Scanner
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenSearchForward
from Vintageous.ex.parsers.new.tokens import TokenSearchBackward
from Vintageous.ex.parsers.new.tokens import TokenDollar
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens import TokenMark
from Vintageous.ex.parsers.new.tokens import TokenComma
from Vintageous.ex.parsers.new.tokens import TokenSemicolon


class parse_line_ref_Tests(unittest.TestCase):
    def test_CanParseEmpty(self):
        parsed = start_parsing('')
        self.assertEqual(parsed.line_range, None)
        self.assertEqual(parsed.command, None)

    def test_CanParseDotAsStartLine(self):
        parsed = start_parsing('.')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseDotWithOffset(self):
        parsed = start_parsing('.+10')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseLoneOffset(self):
        parsed = start_parsing('+10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_FailsIfDotAfterOffset(self):
        self.assertRaises(ValueError, start_parsing, '+10.')

    def test_CanParseMultipleOffsets(self):
        parsed = start_parsing('+10+10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchForward(self):
        parsed = start_parsing('/foo/')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_SearchForwardClearsPreviousReferences(self):
        parsed = start_parsing('./foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchForward ('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_SearchForwardClearsPreviousReferencesWithOffsets(self):
        parsed = start_parsing('.+10/foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchBackward(self):
        parsed = start_parsing('?foo?')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_SearchBackwardClearsPreviousReferences(self):
        parsed = start_parsing('.?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_SearchBackwardClearsPreviousReferencesWithOffsets(self):
        parsed = start_parsing('.+10?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchForwardWithOffset(self):
        parsed = start_parsing('/foo/+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchForwardWithOffsets(self):
        parsed = start_parsing('/foo/+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10, 10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchBacwardWithOffset(self):
        parsed = start_parsing('?foo?+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseSearchBacwardWithOffsets(self):
        parsed = start_parsing('?foo?+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10, 10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])

    def test_CanParseDollarOnItsOwn(self):
        parsed = start_parsing('$')
        self.assertEqual(parsed.line_range.start, [TokenDollar()])

    def test_CanParseDollarWithCompany(self):
        parsed = start_parsing('0,$')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])

    def test_FailsIfDollarOffset(self):
        self.assertRaises(ValueError, start_parsing, '$+10')

    def test_FailsIfPrecededByAnything(self):
        self.assertRaises(ValueError, start_parsing, '.$')
        self.assertRaises(ValueError, start_parsing, '/foo/$')
        self.assertRaises(ValueError, start_parsing, '100$')

    def test_CanParseLoneComma(self):
        parsed = start_parsing(',')
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseDotComma(self):
        parsed = start_parsing('.,')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseCommaDot(self):
        parsed = start_parsing(',.')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])

    def test_CanParseLoneSmicolon(self):
        parsed = start_parsing(';')
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseDotSmicolon(self):
        parsed = start_parsing('.;')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseSmicolonDot(self):
        parsed = start_parsing(';.')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseCommaOffset(self):
        parsed = start_parsing(',+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseSemicolonOffset(self):
        parsed = start_parsing(';+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseOffsetCommaOffset(self):
        parsed = start_parsing('+10,+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseSemicolonOffset(self):
        parsed = start_parsing('+10;+10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [10])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseNumber(self):
        parsed = start_parsing('10')
        self.assertEqual(parsed.line_range.start, [TokenDigits('10')])

    def test_CanParseNumberRightHandSide(self):
        parsed = start_parsing(',10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDigits('10')])

    def test_FailsIfDotDigits(self):
        self.assertRaises(ValueError, start_parsing, '.10')


class parse_line_ref_TokenComma_Tests(unittest.TestCase):
    def test_CanParseLongSequence(self):
        # Vim allows this.
        parsed = start_parsing('1,2,3,4')
        self.assertEqual(parsed.line_range.start, [TokenDigits('3')])
        self.assertEqual(parsed.line_range.end, [TokenDigits('4')])


class parse_line_ref_ParseSubstituteCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = start_parsing('substitute')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseAlias(self):
        parsed = start_parsing('s')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSimpleRange(self):
        parsed = start_parsing('4s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithStartAndEndLines(self):
        parsed = start_parsing('4,5s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.line_range.end, [TokenDigits ('5')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchForward(self):
        parsed = start_parsing('/foo/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackward(self):
        parsed = start_parsing('?foo?s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackwardAndSearchForward(self):
        parsed = start_parsing('?foo?,/bar/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.line_range.end, [TokenSearchForward ('bar')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithZeroAndDollar(self):
        parsed = start_parsing('0,$s')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])
        self.assertEqual(parsed.command.content, 'substitute')


class parse_line_ref_SetLineRangeSeparator(unittest.TestCase):
    def test_CanSetComma(self):
        parsed = start_parsing(",")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolon(self):
        parsed = start_parsing(";")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetCommaMultipleTimes(self):
        parsed = start_parsing("1,2,3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolonMultipleTimes(self):
        parsed = start_parsing("1;2;3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesSemicolonLast(self):
        parsed = start_parsing("1;2,3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesCommaLast(self):
        parsed = start_parsing("1;2;3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())


class parse_line_ref_ParseMarks(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = start_parsing("'a")
        self.assertEqual(parsed.line_range.start, [TokenMark('a')])

    def test_CanParseOnTwoSides(self):
        parsed = start_parsing("'a,'b")
        self.assertEqual(parsed.line_range.start, [TokenMark ('a')])
        self.assertEqual(parsed.line_range.end, [TokenMark ('b')])
