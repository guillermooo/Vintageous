import unittest

from Vintageous.ex.parser.parser import parse_command_line
from Vintageous.ex.parser.scanner import Scanner
from Vintageous.ex.parser.tokens import TokenDot
from Vintageous.ex.parser.tokens import TokenSearchForward
from Vintageous.ex.parser.tokens import TokenSearchBackward
from Vintageous.ex.parser.tokens import TokenDollar
from Vintageous.ex.parser.tokens import TokenDigits
from Vintageous.ex.parser.tokens import TokenPercent
from Vintageous.ex.parser.tokens import TokenMark
from Vintageous.ex.parser.tokens import TokenOffset
from Vintageous.ex.parser.tokens import TokenComma
from Vintageous.ex.parser.tokens import TokenSemicolon


class parse_line_ref_Tests(unittest.TestCase):
    def test_CanParseEmpty(self):
        parsed = parse_command_line('')
        self.assertEqual(parsed.line_range, None)
        self.assertEqual(parsed.command, None)

    def test_CanParseDotAsStartLine(self):
        parsed = parse_command_line('.')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseDotWithOffset(self):
        parsed = parse_command_line('.+10')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseLoneOffset(self):
        parsed = parse_command_line('+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_FailsIfDotAfterOffset(self):
        self.assertRaises(ValueError, parse_command_line, '+10.')

    def test_CanParseMultipleOffsets(self):
        parsed = parse_command_line('+10+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForward(self):
        parsed = parse_command_line('/foo/')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchForwardClearsPreviousReferences(self):
        parsed = parse_command_line('./foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchForward ('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchForwardClearsPreviousReferencesWithOffsets(self):
        parsed = parse_command_line('.+10/foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10]), TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBackward(self):
        parsed = parse_command_line('?foo?')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchBackwardClearsPreviousReferences(self):
        parsed = parse_command_line('.?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchBackwardClearsPreviousReferencesWithOffsets(self):
        parsed = parse_command_line('.+10?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10]), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForwardWithOffset(self):
        parsed = parse_command_line('/foo/+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo'), TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForwardWithOffsets(self):
        parsed = parse_command_line('/foo/+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo'), TokenOffset ([10, 10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBacwardWithOffset(self):
        parsed = parse_command_line('?foo?+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo'), TokenOffset ([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBacwardWithOffsets(self):
        parsed = parse_command_line('?foo?+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo'), TokenOffset ([10, 10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseDollarOnItsOwn(self):
        parsed = parse_command_line('$')
        self.assertEqual(parsed.line_range.start, [TokenDollar()])

    def test_CanParseDollarWithCompany(self):
        parsed = parse_command_line('0,$')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])

    def test_FailsIfDollarOffset(self):
        self.assertRaises(ValueError, parse_command_line, '$+10')

    def test_FailsIfPrecededByAnything(self):
        self.assertRaises(ValueError, parse_command_line, '.$')
        self.assertRaises(ValueError, parse_command_line, '/foo/$')
        self.assertRaises(ValueError, parse_command_line, '100$')

    def test_CanParseLoneComma(self):
        parsed = parse_command_line(',')
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseDotComma(self):
        parsed = parse_command_line('.,')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseCommaDot(self):
        parsed = parse_command_line(',.')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])

    def test_CanParseLoneSmicolon(self):
        parsed = parse_command_line(';')
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseDotSmicolon(self):
        parsed = parse_command_line('.;')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseSmicolonDot(self):
        parsed = parse_command_line(';.')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseCommaOffset(self):
        parsed = parse_command_line(',+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenOffset([10])])

    def test_CanParseSemicolonOffset(self):
        parsed = parse_command_line(';+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseOffsetCommaOffset(self):
        parsed = parse_command_line('+10,+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [TokenOffset ([10])])

    def test_CanParseSemicolonOffset(self):
        parsed = parse_command_line('+10;+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseNumber(self):
        parsed = parse_command_line('10')
        self.assertEqual(parsed.line_range.start, [TokenDigits('10')])

    def test_CanParseNumberRightHandSide(self):
        parsed = parse_command_line(',10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDigits('10')])

    def test_FailsIfDotDigits(self):
        self.assertRaises(ValueError, parse_command_line, '.10')


class parse_line_ref_TokenComma_Tests(unittest.TestCase):
    def test_CanParseLongSequence(self):
        # Vim allows this.
        parsed = parse_command_line('1,2,3,4')
        self.assertEqual(parsed.line_range.start, [TokenDigits('3')])
        self.assertEqual(parsed.line_range.end, [TokenDigits('4')])


class parse_line_ref_ParseSubstituteCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_command_line('substitute')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseAlias(self):
        parsed = parse_command_line('s')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSimpleRange(self):
        parsed = parse_command_line('4s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithStartAndEndLines(self):
        parsed = parse_command_line('4,5s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.line_range.end, [TokenDigits ('5')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchForward(self):
        parsed = parse_command_line('/foo/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackward(self):
        parsed = parse_command_line('?foo?s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackwardAndSearchForward(self):
        parsed = parse_command_line('?foo?,/bar/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.line_range.end, [TokenSearchForward ('bar')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithZeroAndDollar(self):
        parsed = parse_command_line('0,$s')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])
        self.assertEqual(parsed.command.content, 'substitute')


class parse_line_ref_Percent(unittest.TestCase):
    def test_CanParsePercent(self):
        parsed = parse_command_line("%")
        self.assertEqual(parsed.line_range.start, [TokenPercent()])


class parse_line_ref_SetLineRangeSeparator(unittest.TestCase):
    def test_CanSetComma(self):
        parsed = parse_command_line(",")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolon(self):
        parsed = parse_command_line(";")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetCommaMultipleTimes(self):
        parsed = parse_command_line("1,2,3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolonMultipleTimes(self):
        parsed = parse_command_line("1;2;3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesSemicolonLast(self):
        parsed = parse_command_line("1;2,3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesCommaLast(self):
        parsed = parse_command_line("1;2;3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())


class parse_line_ref_ParseMarks(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_command_line("'a")
        self.assertEqual(parsed.line_range.start, [TokenMark('a')])

    def test_CanParseOnTwoSides(self):
        parsed = parse_command_line("'a,'b")
        self.assertEqual(parsed.line_range.start, [TokenMark ('a')])
        self.assertEqual(parsed.line_range.end, [TokenMark ('b')])


class parse_line_ref_ParseOnlyCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_command_line('only')
        self.assertEqual(parsed.command.content, 'only')

    def test_CanParseAlias(self):
        parsed = parse_command_line('on')
        self.assertEqual(parsed.command.content, 'only')


class parse_line_ref_ParseRegistersCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_command_line('registers')
        self.assertEqual(parsed.command.content, 'registers')

    def test_CanParseAlias(self):
        parsed = parse_command_line('reg')
        self.assertEqual(parsed.command.content, 'registers')


class parse_line_ref_ParseWriteCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_command_line('write')
        self.assertEqual(parsed.command.content, 'write')

    def test_CanParseAlias(self):
        parsed = parse_command_line('w')
        self.assertEqual(parsed.command.content, 'write')