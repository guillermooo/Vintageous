import unittest

from Vintageous.ex.parsers.new.parser import parse_ex_command
from Vintageous.ex.parsers.new.scanner import Scanner
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenSearchForward
from Vintageous.ex.parsers.new.tokens import TokenSearchBackward
from Vintageous.ex.parsers.new.tokens import TokenDollar
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens import TokenMark
from Vintageous.ex.parsers.new.tokens import TokenOffset
from Vintageous.ex.parsers.new.tokens import TokenComma
from Vintageous.ex.parsers.new.tokens import TokenSemicolon


class parse_line_ref_Tests(unittest.TestCase):
    def test_CanParseEmpty(self):
        parsed = parse_ex_command('')
        self.assertEqual(parsed.line_range, None)
        self.assertEqual(parsed.command, None)

    def test_CanParseDotAsStartLine(self):
        parsed = parse_ex_command('.')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseDotWithOffset(self):
        parsed = parse_ex_command('.+10')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseLoneOffset(self):
        parsed = parse_ex_command('+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_FailsIfDotAfterOffset(self):
        self.assertRaises(ValueError, parse_ex_command, '+10.')

    def test_CanParseMultipleOffsets(self):
        parsed = parse_ex_command('+10+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForward(self):
        parsed = parse_ex_command('/foo/')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchForwardClearsPreviousReferences(self):
        parsed = parse_ex_command('./foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchForward ('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchForwardClearsPreviousReferencesWithOffsets(self):
        parsed = parse_ex_command('.+10/foo/')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10]), TokenSearchForward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBackward(self):
        parsed = parse_ex_command('?foo?')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchBackwardClearsPreviousReferences(self):
        parsed = parse_ex_command('.?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_SearchBackwardClearsPreviousReferencesWithOffsets(self):
        parsed = parse_ex_command('.+10?foo?')
        self.assertEqual(parsed.line_range.start, [TokenDot(), TokenOffset([10]), TokenSearchBackward('foo')])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForwardWithOffset(self):
        parsed = parse_ex_command('/foo/+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo'), TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchForwardWithOffsets(self):
        parsed = parse_ex_command('/foo/+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward('foo'), TokenOffset ([10, 10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBacwardWithOffset(self):
        parsed = parse_ex_command('?foo?+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo'), TokenOffset ([10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseSearchBacwardWithOffsets(self):
        parsed = parse_ex_command('?foo?+10+10+10')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward('foo'), TokenOffset ([10, 10, 10])])
        self.assertEqual(parsed.line_range.end, [])

    def test_CanParseDollarOnItsOwn(self):
        parsed = parse_ex_command('$')
        self.assertEqual(parsed.line_range.start, [TokenDollar()])

    def test_CanParseDollarWithCompany(self):
        parsed = parse_ex_command('0,$')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])

    def test_FailsIfDollarOffset(self):
        self.assertRaises(ValueError, parse_ex_command, '$+10')

    def test_FailsIfPrecededByAnything(self):
        self.assertRaises(ValueError, parse_ex_command, '.$')
        self.assertRaises(ValueError, parse_ex_command, '/foo/$')
        self.assertRaises(ValueError, parse_ex_command, '100$')

    def test_CanParseLoneComma(self):
        parsed = parse_ex_command(',')
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseDotComma(self):
        parsed = parse_ex_command('.,')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanParseCommaDot(self):
        parsed = parse_ex_command(',.')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])

    def test_CanParseLoneSmicolon(self):
        parsed = parse_ex_command(';')
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseDotSmicolon(self):
        parsed = parse_ex_command('.;')
        self.assertEqual(parsed.line_range.start, [TokenDot()])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseSmicolonDot(self):
        parsed = parse_ex_command(';.')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDot()])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseCommaOffset(self):
        parsed = parse_ex_command(',+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenOffset([10])])

    def test_CanParseSemicolonOffset(self):
        parsed = parse_ex_command(';+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseOffsetCommaOffset(self):
        parsed = parse_ex_command('+10,+10')
        self.assertEqual(parsed.line_range.separator, TokenComma())
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [TokenOffset ([10])])

    def test_CanParseSemicolonOffset(self):
        parsed = parse_ex_command('+10;+10')
        self.assertEqual(parsed.line_range.start, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.end, [TokenOffset([10])])
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanParseNumber(self):
        parsed = parse_ex_command('10')
        self.assertEqual(parsed.line_range.start, [TokenDigits('10')])

    def test_CanParseNumberRightHandSide(self):
        parsed = parse_ex_command(',10')
        self.assertEqual(parsed.line_range.start, [])
        self.assertEqual(parsed.line_range.end, [TokenDigits('10')])

    def test_FailsIfDotDigits(self):
        self.assertRaises(ValueError, parse_ex_command, '.10')


class parse_line_ref_TokenComma_Tests(unittest.TestCase):
    def test_CanParseLongSequence(self):
        # Vim allows this.
        parsed = parse_ex_command('1,2,3,4')
        self.assertEqual(parsed.line_range.start, [TokenDigits('3')])
        self.assertEqual(parsed.line_range.end, [TokenDigits('4')])


class parse_line_ref_ParseSubstituteCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_ex_command('substitute')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseAlias(self):
        parsed = parse_ex_command('s')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSimpleRange(self):
        parsed = parse_ex_command('4s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithStartAndEndLines(self):
        parsed = parse_ex_command('4,5s')
        self.assertEqual(parsed.line_range.start, [TokenDigits ('4')])
        self.assertEqual(parsed.line_range.end, [TokenDigits ('5')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchForward(self):
        parsed = parse_ex_command('/foo/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchForward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackward(self):
        parsed = parse_ex_command('?foo?s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackwardAndSearchForward(self):
        parsed = parse_ex_command('?foo?,/bar/s')
        self.assertEqual(parsed.line_range.start, [TokenSearchBackward ('foo')])
        self.assertEqual(parsed.line_range.end, [TokenSearchForward ('bar')])
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithZeroAndDollar(self):
        parsed = parse_ex_command('0,$s')
        self.assertEqual(parsed.line_range.start, [TokenDigits('0')])
        self.assertEqual(parsed.line_range.end, [TokenDollar()])
        self.assertEqual(parsed.command.content, 'substitute')


class parse_line_ref_SetLineRangeSeparator(unittest.TestCase):
    def test_CanSetComma(self):
        parsed = parse_ex_command(",")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolon(self):
        parsed = parse_ex_command(";")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetCommaMultipleTimes(self):
        parsed = parse_ex_command("1,2,3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())

    def test_CanSetSemicolonMultipleTimes(self):
        parsed = parse_ex_command("1;2;3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesSemicolonLast(self):
        parsed = parse_ex_command("1;2,3;4")
        self.assertEqual(parsed.line_range.separator, TokenSemicolon())

    def test_CanSetMultipleTimesCommaLast(self):
        parsed = parse_ex_command("1;2;3,4")
        self.assertEqual(parsed.line_range.separator, TokenComma())


class parse_line_ref_ParseMarks(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = parse_ex_command("'a")
        self.assertEqual(parsed.line_range.start, [TokenMark('a')])

    def test_CanParseOnTwoSides(self):
        parsed = parse_ex_command("'a,'b")
        self.assertEqual(parsed.line_range.start, [TokenMark ('a')])
        self.assertEqual(parsed.line_range.end, [TokenMark ('b')])
